# Site Moto S. Cristóvão

Site estático (sem base de dados) com painel de gestão em `/admin` (Decap CMS), alojado no Netlify a partir de um repositório GitHub. Cada alteração feita no painel fica guardada no GitHub e o Netlify volta a publicar o site sozinho (~1 minuto).

## Estrutura
| Pasta / ficheiro | O quê |
|---|---|
| `content/motas/*.json` | Uma ficha por mota nova (editável no painel) |
| `content/usadas/*.json` | Uma ficha por mota usada (editável no painel) |
| `content/site.json` | Telefone, email, horário, WhatsApp, redes sociais (editável no painel) |
| `src/assets/fotos/` | Fotos. As carregadas no painel vão para `uploads/` |
| `src/data/marcas.json` | Marcas, cores, logótipos e ordem dos segmentos |
| `src/admin/` | Painel de gestão (Decap CMS) |
| `build.py` | Gera o site em `dist/` e otimiza as fotos (WebP 1600 px e 640 px) |
| `netlify.toml` | Configuração do Netlify (comando, pasta, cabeçalhos de segurança, modo pré-visualização) |

Gerar localmente: `pip install Pillow` e depois `python3 build.py` (ou `PREVIEW=1 python3 build.py`).

## Pôr online (uma vez)
1. **GitHub** — criar um repositório privado (ex.: `site-moto-sao-cristovao`) e carregar todo o conteúdo desta pasta (exceto `dist/` e `dist-preview/`).
2. **Netlify** — *Add new project → Import an existing project → GitHub* → escolher o repositório. O Netlify lê o `netlify.toml` sozinho; carregar em *Deploy*.
3. **Ativar o painel** — no projeto Netlify:
   - *Project configuration → Identity → Enable Identity*.
   - *Registration preferences* → **Invite only** (ninguém se regista sozinho).
   - *Services → Git Gateway → Enable*.
   - *Identity → Invite users* → convidar o email do stand (e o teu). O convidado recebe um email, define a palavra-passe e entra em `/admin`.
4. **Domínio** — *Domain management → Add a domain* → `motosaocristovao.pt` e seguir as instruções de DNS no registo do domínio. O certificado HTTPS é automático.
5. **Quando o stand aprovar** — no `netlify.toml` mudar `PREVIEW = "1"` para `PREVIEW = "0"` (tira a faixa amarela e deixa o Google indexar).

## Segurança
- Sem base de dados nem formulários públicos: o site não guarda dados de clientes.
- Painel só por convite; ativar verificação em dois passos no GitHub e no Netlify.
- Cabeçalhos de segurança em `netlify.toml` e CSP em cada página (sem scripts externos no site público).

## Custos
Domínio (já pago pelo stand). GitHub, Netlify (plano gratuito) e Decap CMS: 0 €.
