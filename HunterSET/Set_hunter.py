from sclib import SoundcloudAPI, Track

# --- MUDANÇA PRINCIPAL AQUI ---
# Dividimos a lista para tratar cada caso com a ferramenta certa.
LISTA_DE_ARTISTAS = [
    "elinasounds",  # Nome de usuário da E.Lina no SoundCloud
    "parsec-music-official",  # Nome de usuário do Parsec
    "crihan"  # Nome de usuário do Crihan
]
# LISTA_DE_KEYWORDS = ["minimal", "romania", "microhouse"] # Vamos tratar depois

DURACAO_MINIMA_MS = 30 * 60 * 1000


def formatar_duracao(ms):
    """Função auxiliar para converter a duração de milissegundos."""
    if not ms: return "N/A"
    segundos_totais = int(ms / 1000)
    horas = segundos_totais // 3600
    minutos = (segundos_totais % 3600) // 60
    segundos = segundos_totais % 60
    if horas > 0:
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    return f"{minutos:02d}:{segundos:02d}"


def buscar_sets_por_artista():
    """
    Busca os sets mais recentes dos artistas especificados.
    """
    print("🤖 Iniciando o Set Hunter Bot (v4.0 - Artist Fetcher)...")

    api = SoundcloudAPI()

    for nome_artista in LISTA_DE_ARTISTAS:
        print(f"\n🔎 Procurando sets do artista: '{nome_artista}'")
        try:
            # --- MUDANÇA PRINCIPAL AQUI ---
            # Usamos .resolve() para encontrar o artista pelo seu nome de usuário
            artista = api.resolve(f"https://soundcloud.com/{nome_artista}")

            if not artista:
                print(f"   -> Artista '{nome_artista}' não encontrado.")
                continue

            # Pegamos todas as faixas do artista
            todas_as_faixas = artista.get_tracks()

            sets_encontrados = []
            for track in todas_as_faixas:
                # Verificamos a duração para encontrar os sets
                if track.duration and track.duration >= DURACAO_MINIMA_MS:
                    sets_encontrados.append(track)

                # Paramos quando encontrarmos os 5 sets mais recentes
                if len(sets_encontrados) >= 5:
                    break

            if not sets_encontrados:
                print(f"   -> Nenhum set longo encontrado para '{nome_artista}'.")
                continue

            print(f"   -> Sets recentes de '{nome_artista}':")
            for set_track in sets_encontrados:
                print(f"   🎵 Título: {set_track.title}")
                print(f"      - Duração: {formatar_duracao(set_track.duration)}")
                print(f"      - Link: {set_track.permalink_url}")

        except Exception as e:
            print(f"   ❌ Ocorreu um erro inesperado ao buscar por '{nome_artista}': {e}")

    print("\n✅ Busca por artistas finalizada.")


if __name__ == "__main__":
    buscar_sets_por_artista()
    print("\nℹ️ A busca por keywords como 'minimal' será implementada a seguir.")