import requests
import config


LISTA_DE_ARTISTAS = [
    "elinaelian",
    "parsec_dj",
    "olga-korol",
    "cristi-cons",
]

DURACAO_MINIMA_MS = 30 * 60 * 1000

def formatar_duracao(ms):
    if not ms: return "N/A"
    segundos_totais = int(ms / 1000)
    horas = segundos_totais // 3600
    minutos = (segundos_totais % 3600) // 60
    segundos = segundos_totais % 60
    if horas > 0:
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    return f"{minutos:02d}:{segundos:02d}"

def buscar_sets_direto_api():
    print("🤖 Iniciando o Set Hunter (v.Final - API Direta)...")

    client_id = config.CLIENT_ID
    headers = {'User-Agent': 'Mozilla/5.0'}

    for username in LISTA_DE_ARTISTAS:
        print(f"\n🔎 Processando o artista: '{username}'")
        try:
            # --- PASSO 1: Descobrir o ID do utilizador a partir do nome ---
            print("   - Resolvendo ID do artista...")
            resolve_url = f"https://api-v2.soundcloud.com/resolve?url=https://soundcloud.com/{username}&client_id={client_id}"
            response = requests.get(resolve_url, headers=headers)
            response.raise_for_status()

            user_data = response.json()
            user_id = user_data.get('id')

            if not user_id:
                print(f"   -> Não foi possível encontrar o ID para o artista '{username}'.")
                continue

            print(f"   - ID encontrado: {user_id}")

            print("   - Buscando faixas do artista...")
            tracks_url = f"https://api-v2.soundcloud.com/users/{user_id}/tracks?limit=200&client_id={client_id}"
            response = requests.get(tracks_url, headers=headers)
            response.raise_for_status()

            tracks_data = response.json()
            collection = tracks_data.get('collection', [])

            if not collection:
                print(f"   -> Nenhuma faixa encontrada para '{username}'.")
                continue

            # --- PASSO 3: Filtrar as faixas para encontrar os sets ---
            print(f"   - {len(collection)} faixas encontradas. Filtrando por duração...")
            sets_encontrados = []
            for track in collection:
                if track.get('duration', 0) >= DURACAO_MINIMA_MS:
                    sets_encontrados.append(track)
                if len(sets_encontrados) >= 5:
                    break

            if not sets_encontrados:
                print(f"   -> Nenhum set longo encontrado para '{username}'.")
                continue

            # --- PASSO 4: Imprimir os resultados ---
            print(f"   -> Sets recentes de '{username}':")
            for set_track in sets_encontrados:
                print(f"   🎵 Título: {set_track.get('title')}")
                print(f"      - Duração: {formatar_duracao(set_track.get('duration'))}")
                print(f"      - Link: {set_track.get('permalink_url')}")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"   ❌ Erro: Artista '{username}' não encontrado (404). Verifique o nome de utilizador.")
            else:
                print(f"   ❌ Erro de HTTP ao processar '{username}': {e}")
        except Exception as e:
            print(f"   ❌ Ocorreu um erro inesperado ao processar '{username}': {e}")

    print("\n✅ Bot finalizado.")


if __name__ == "__main__":
    buscar_sets_direto_api()