# teste_api.py (v3 - Usando a Biblioteca Oficial Direta)

import google.generativeai as genai
import config


def testar_api_google_direto():

    print("Iniciando teste de conexão (Método Direto)...")

    if not hasattr(config, 'GOOGLE_API_KEY') or "SUA_CHAVE" in config.GOOGLE_API_KEY:
        print("\nERRO: A sua GOOGLE_API_KEY não parece estar configurada no ficheiro config.py.")
        return

    try:
        # Passo 1: Configurar a biblioteca com a nossa chave
        genai.configure(api_key=config.GOOGLE_API_KEY)
        print(" Chave da API configurada com sucesso.")

        # Passo 2: Criar uma instância do modelo
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print(" Modelo 'gemini-1.5-flash' instanciado.")

        # Passo 3: Enviar o prompt de teste
        print("... Enviando um prompt de teste...")
        response = model.generate_content("Responda apenas com a palavra 'sucesso'.")

        # Passo 4: Imprimir a resposta
        print("\nSUCESSO! A API respondeu!")
        print(f"   -> Resposta do modelo: '{response.text}'")

    except Exception as e:
        print("\nFALHA NA CONEXÃO. Ocorreu um erro durante o teste.")
        print(f"   -> Tipo de Erro: {type(e).__name__}")
        print(f"   -> Detalhes: {e}")


if __name__ == "__main__":
    testar_api_google_direto()