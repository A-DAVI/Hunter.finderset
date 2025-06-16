# Hunter.finderset
Projeto: Curador de Sets Inteligente

Este é um bot de automação em Python desenhado para descobrir e catalogar DJ sets de música eletrónica a partir do SoundCloud. As suas principais funcionalidades incluem:

Busca por Artistas: Monitoriza uma lista de artistas preferidos, buscando os seus sets mais recentes de longa duração.

Curadoria com IA: Utiliza a API do Gemini para analisar cada set, gerando tags de estilo e recomendando artistas similares para expandir a descoberta.

Sistema de Aprendizagem: Mantém uma "memória" através de ficheiros de texto, adicionando automaticamente novos artistas recomendados à sua lista de busca.

Auto-Otimização: Coloca em "blacklist" artistas que não existem (erro 404) e em "quarentena" artistas que não têm conteúdo relevante, tornando as buscas futuras mais eficientes.

Filtros Personalizados: Permite filtrar os sets por critérios como BPM, ignorando o que não se alinha com o gosto do utilizador.

Integração com Notion: Envia todos os dados recolhidos e analisados — incluindo título, artista, link, duração, BPM, capa do set e as análises da IA — para uma base de dados do Notion, criando uma biblioteca de música visual e organizada.
