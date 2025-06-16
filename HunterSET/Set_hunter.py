import requests
import config
import json
import google.generativeai as genai
import os
import time
import notion_client

try:
    genai.configure(api_key=config.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("Modelo de IA 'gemini-1.5-flash' carregado e pronto.")
except Exception as e:
    model = None
    print(f"Erro ao configurar a API do Gemini: {e}")

try:
    notion = notion_client.Client(auth=config.NOTION_API_KEY)
    DATABASE_ID = config.NOTION_DATABASE_ID
    print("Cliente Notion inicializado com sucesso.")
except Exception as e:
    notion = None
    DATABASE_ID = None
    print(f"Erro ao configurar a API do Notion: {e}")

NOME_FICHEIRO_ARTISTAS = "artistas.txt"
NOME_FICHEIRO_BLACKLIST = "blacklist.txt"
NOME_FICHEIRO_QUARENTENA = "quarentena.txt"
NOME_FICHEIRO_LOG_NOTION = "log_sets_adicionados.txt"

DURACAO_MINIMA_MS = 30 * 60 * 1000
BPM_MINIMO = 124
BPM_MAXIMO = 135


def carregar_set_de_ficheiro(caminho_ficheiro):
    if not os.path.exists(caminho_ficheiro):
        return set()
    with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
        itens = {linha.strip().lower() for linha in f if linha.strip()}
    print(f"Carregados {len(itens)} itens de '{caminho_ficheiro}'.")
    return itens


def salvar_set_em_ficheiro(caminho_ficheiro, itens_para_salvar):
    with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
        for item in sorted(list(itens_para_salvar)):
            f.write(f"{item}\n")
    print(f"Lista atualizada e salva em '{caminho_ficheiro}'. Total: {len(itens_para_salvar)} itens.")


def logar_set_adicionado(caminho_ficheiro, link_do_set):
    with open(caminho_ficheiro, 'a', encoding='utf-8') as f:
        f.write(f"{link_do_set.lower()}\n")


def adicionar_set_ao_notion(titulo, artista, link, duracao, bpm, tags_ia, artistas_similares, artwork_url):
    if not notion or not DATABASE_ID:
        print("   [Aviso Notion] Cliente Notion ou ID da Base de Dados não configurado. Pulando envio.")
        return False
    try:
        propriedades = {
            "Título": {"title": [{"text": {"content": titulo}}]},
            "Artista": {"rich_text": [{"text": {"content": artista}}]},
            "Link": {"url": link},
            "Duração": {"rich_text": [{"text": {"content": duracao}}]},
            "Tags IA": {"multi_select": [{"name": tag} for tag in tags_ia]},
            "Artistas Similares": {"multi_select": [{"name": nome} for nome in artistas_similares]},
        }
        if bpm:
            propriedades["BPM"] = {"number": float(bpm)}

        cover_data = {"type": "external", "external": {"url": artwork_url}}

        print("   -> Enviando para o Notion...")
        notion.pages.create(parent={"database_id": DATABASE_ID}, properties=propriedades, cover=cover_data)
        print("   Set adicionado com sucesso ao Notion!")
        return True
    except Exception as e:
        print(f"   Erro ao enviar para o Notion: {e}")
        return False


def gerar_analise_com_ia(titulo_set, nome_artista):
    if not model:
        return [], []
    prompt = f"""Aja como um especialista em música eletrónica underground. Analise o seguinte set com base no seu título e artista: - Artista: "{nome_artista}" - Título: "{titulo_set}". Forneça a sua análise num objeto JSON com duas chaves: 1. "tags": uma lista de 5 tags de estilo ou "vibe". 2. "artistas_similares": uma lista de 3 outros artistas com um som semelhante."""
    try:
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)
        response_dict = json.loads(response.text)
        return response_dict.get("tags", []), response_dict.get("artistas_similares", [])
    except Exception as e:
        print(f"      [Aviso IA] Não foi possível gerar análise. Erro: {e}")
        return [], []


def formatar_duracao(ms):
    if not ms: return "N/A"
    segundos_totais = int(ms / 1000);
    horas = segundos_totais // 3600;
    minutos = (segundos_totais % 3600) // 60;
    segundos = segundos_totais % 60
    if horas > 0: return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    return f"{minutos:02d}:{segundos:02d}"


def obter_artwork_maior(url_artwork):
    if not url_artwork: return "https://i.imgur.com/sC4JCIa.png"
    return url_artwork.replace("large.jpg", "t500x500.jpg")


def bot_cacador_final():
    print("\nIniciando o Bot Caçador...")

    artistas_do_ficheiro = carregar_set_de_ficheiro(NOME_FICHEIRO_ARTISTAS)
    blacklist = carregar_set_de_ficheiro(NOME_FICHEIRO_BLACKLIST)
    quarentena = carregar_set_de_ficheiro(NOME_FICHEIRO_QUARENTENA)
    sets_ja_no_notion = carregar_set_de_ficheiro(NOME_FICHEIRO_LOG_NOTION)

    artistas_a_ignorar = blacklist.union(quarentena)
    lista_de_artistas_a_procurar = list(artistas_do_ficheiro - artistas_a_ignorar)

    if lista_de_artistas_a_procurar:
        print(f"{len(artistas_a_ignorar)} artistas na blacklist/quarentena foram ignorados.")

    novos_para_blacklist = set();
    novos_para_quarentena = set();
    artistas_recomendados_geral = set()
    client_id = config.CLIENT_ID;
    headers = {'User-Agent': 'Mozilla/5.0'}

    if not lista_de_artistas_a_procurar:
        print("Lista de artistas vazia ou todos os artistas estão em listas de exclusão.")
    else:
        print("\n" + "=" * 40 + "\nPROCESSANDO ARTISTAS\n" + "=" * 40)
        for username in lista_de_artistas_a_procurar:
            print(f"\nProcessando o artista: '{username}'")
            try:
                resolve_url = f"https://api-v2.soundcloud.com/resolve?url=https://soundcloud.com/{username}&client_id={client_id}"
                response = requests.get(resolve_url, headers=headers);
                response.raise_for_status()
                user_id = response.json().get('id')
                if not user_id: continue

                tracks_url = f"https://api-v2.soundcloud.com/users/{user_id}/tracks?limit=200&client_id={client_id}"
                response = requests.get(tracks_url, headers=headers);
                response.raise_for_status()
                sets_encontrados = [t for t in response.json().get('collection', []) if
                                    t.get('duration', 0) >= DURACAO_MINIMA_MS]

                if not sets_encontrados:
                    print(f"   -> Nenhum set longo encontrado. Artista '{username}' movido para a quarentena.");
                    novos_para_quarentena.add(username)
                    continue

                print(f"   -> Encontrados {len(sets_encontrados)} sets longos. Processando até 5...")
                for set_track in sets_encontrados[:5]:
                    link = set_track.get('permalink_url')
                    if link and link.lower() in sets_ja_no_notion:
                        print(f"   -> Set '{set_track.get('title')}' já está no Notion. Pulando.")
                        continue

                    titulo = set_track.get('title');
                    artista = set_track.get('user', {}).get('username', '');
                    bpm = set_track.get('bpm')

                    if bpm and (bpm < BPM_MINIMO or bpm > BPM_MAXIMO):
                        print(f"   Set '{titulo}' reciclado (BPM de {bpm}).");
                        continue

                    print(f"   Análise para: {titulo}");
                    tags_ia, artistas_similares = gerar_analise_com_ia(titulo, artista)
                    if artistas_similares: artistas_recomendados_geral.update(artistas_similares)

                    artwork = obter_artwork_maior(set_track.get('artwork_url'))
                    sucesso_envio = adicionar_set_ao_notion(titulo, artista, link,
                                                            formatar_duracao(set_track.get('duration')), bpm, tags_ia,
                                                            artistas_similares, artwork)

                    if sucesso_envio:
                        logar_set_adicionado(NOME_FICHEIRO_LOG_NOTION, link)
                        sets_ja_no_notion.add(link.lower())

                    print("      - Aguardando 4s para respeitar o limite da API...");
                    time.sleep(4)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"   Erro 404. '{username}' adicionado à blacklist.");
                    novos_para_blacklist.add(username)
                else:
                    print(f"   Erro HTTP: {e}")
            except Exception as e:
                print(f"   Erro inesperado: {e}")

    print("\n" + "=" * 40 + "\nRESUMO FINAL DA DESCOBERTA\n" + "=" * 40)

    blacklist_final = blacklist.union(novos_para_blacklist)
    quarentena_final = quarentena.union(novos_para_quarentena)
    artistas_finais_limpos = (artistas_do_ficheiro.union(
        artistas_recomendados_geral)) - blacklist_final - quarentena_final

    salvar_set_em_ficheiro(NOME_FICHEIRO_ARTISTAS, artistas_finais_limpos)
    if blacklist_final: salvar_set_em_ficheiro(NOME_FICHEIRO_BLACKLIST, blacklist_final)
    if quarentena_final: salvar_set_em_ficheiro(NOME_FICHEIRO_QUARENTENA, quarentena_final)

    print("\nBot finalizado.")


if __name__ == "__main__":
    bot_cacador_final()