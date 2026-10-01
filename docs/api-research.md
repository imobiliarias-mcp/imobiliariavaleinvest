# Reverse-Engineered API Specification: Imobiliária Vale Invest

## 1. Overview & Architecture

Imobiliária Vale Invest (`https://imobiliariavaleinvest.com.br`) is a prominent real estate agency operating in the Vale do Aço region (Timóteo, Coronel Fabriciano, Ipatinga, and neighboring municipalities in Minas Gerais, Brazil).

The portal is built on top of the **Grupo Union / USO (Union Softwares / BuscaImo)** real estate SaaS engine, hosted on an OpenResty (Nginx) reverse proxy fronting a Node.js / Express web application. The frontend utilizes Semantic UI, Leaflet maps, and Swiper photo carousels with server-side rendered HTML (`text/html; charset=utf-8`) augmented with a dedicated public JSON inventory catalog (`/data/localizacoes.json`) and an NLP term resolution endpoint (`/pesquisar-livre`).

### 1.1 Authentication & Security Requirements
- **Authentication**: **None required**. All rental and sales listing searches, filter queries, pagination offsets, property detail pages, location catalogs, and property images are completely publicly accessible without authentication, session cookies, API keys, or CSRF tokens.
- **Session Cookies**: The server issues standard session cookies (`connect.sid`, `contadorRes`), but state is not required for queries; all searches are fully stateless and reproducible.
- **Request Headers**: Standard desktop `User-Agent` is recommended. No proprietary headers or API tokens are required.
- **HTTP Methods**:
  - Listing Search, Pagination, Filtering, Details, Media, and Facets: `GET`
  - NLP Term Resolution (`/pesquisar-livre`): `POST`

---

## 2. Rental & Sales Search Endpoints

The search engine maps high-level criteria into hierarchical SEO paths and query string parameters.

### 2.1 Canonical Search Routing Pattern

```http
GET /{finalidade}/{uf}/{cidade}/{bairro}/{tipo}/{specs}/ HTTP/1.1
Host: imobiliariavaleinvest.com.br
```

#### Path Segment Definitions
| Segment | Type | Allowed / Example Values | Description |
| :--- | :--- | :--- | :--- |
| `{finalidade}` | `string` | `alugar`, `comprar`, `comprar-ou-alugar`, `temporada`, `permuta`, `imoveis` | Transaction purpose (`alugar` for rentals, `comprar` for sales). |
| `{uf}` *(Optional)* | `string` | `mg`, `ba`, `es` | Two-letter state abbreviation. Automatically precedes `{cidade}`. |
| `{cidade}` *(Optional)* | `string` | `timoteo`, `coronel-fabriciano`, `ipatinga`, `santana-do-paraiso`, etc. | City slug. |
| `{bairro}` *(Optional)* | `string` | `centro`, `funcionarios`, `giovanini`, `floresta`, `belvedere`, etc. | Neighborhood slug. |
| `{tipo}` *(Optional)* | `string` | `apartamento`, `casa`, `ponto`, `sala`, `galpao`, `terreno`, `lote`, `cobertura`, `chacara`, `kitnet` | Property category. |
| `{dormitorios}` *(Optional)* | `string` | `dormitorios-2`, `dormitorios-min_2`, `dormitorios-2_4` | Bedroom constraint. |
| `{valor}` *(Optional)* | `string` | `valor-600_1500`, `valor-min_500`, `valor-max_2000` | Price interval in BRL. |
| `{ordem}` *(Optional)* | `string` | `ordem-valor/resultado-crescente`, `ordem-valor/resultado-decrescente`, `ordem-recentes/resultado-decrescente` | Sorting field and direction. |
| `{quantidade}` *(Optional)* | `string` | `quantidade-12`, `quantidade-24`, `quantidade-36` | Listings per page (default is 12). |
| `{pagina}` *(Optional)* | `string` | `pagina-1`, `pagina-2`, `pagina-3` | 1-indexed page number. |

### 2.2 Target URL Reproduction Analysis

The target URL requested by the user:
```
https://imobiliariavaleinvest.com.br/alugar/mg/timoteo/dormitorios-2/ordem-valor/resultado-crescente/quantidade-12/
```

#### Structural Breakdown:
1. `finalidade`: `alugar` (Rental search)
2. `uf`: `mg` (Minas Gerais state)
3. `cidade`: `timoteo` (Timóteo municipality)
4. `dormitorios`: `dormitorios-2` (Filtered for 2 bedrooms)
5. `ordem`: `ordem-valor` / `resultado-crescente` (Sorted by price, ascending)
6. `quantidade`: `quantidade-12` (12 listings per page)

#### Observed Behavior & Inventory Analysis:
- When querying this exact target URL, the server returns `HTTP 200 OK` with `<input id="countResultado" type="hidden" value="0"/>` and `0` listing cards (`a.link_resultado`).
- Verification against the portal's complete inventory catalog (`/data/localizacoes.json`) reveals that **all active rentals in Timóteo at Vale Invest are commercial points (`PONTO`)** located in the Funcionários neighborhood (e.g. `PT00015`, `PT00016`). Commercial points have 0 bedrooms, so filtering for `dormitorios-2` in Timóteo correctly yields 0 matching properties.
- Querying `/alugar/mg/timoteo/` (without the bedroom constraint) successfully returns both commercial rental listings.
- Querying `/alugar/mg/coronel-fabriciano/dormitorios-min_2/` successfully returns 7 residential properties matching the bedroom filter.

---

## 3. Supporting Endpoints

### 3.1 Taxonomy & Inventory Catalog Endpoint

```http
GET /data/localizacoes.json HTTP/1.1
Host: imobiliariavaleinvest.com.br
```
- **Response Format**: `application/json`
- **Description**: Returns the active property inventory and taxonomy catalog containing 400 entries with municipality, neighborhood, category, transaction flags (`locacao: 1`, `venda: 1`), building name, and development stage.
- **Authentication**: None.

### 3.2 NLP Term Resolution Endpoint

```http
POST /pesquisar-livre HTTP/1.1
Host: imobiliariavaleinvest.com.br
Content-Type: application/x-www-form-urlencoded

finalidade=alugar&tipo=apartamento&termos=fabriciano
```
- **Response Format**: `text/plain`
- **Description**: Translates natural language search terms into canonical SEO URL paths (e.g. `alugar/apartamento/area-rural-de-coronel-fabriciano_nova-fabriciano`).

### 3.3 Direct Reference Search Endpoint

```http
GET /imoveis/referencia-{referencia}/ HTTP/1.1
Host: imobiliariavaleinvest.com.br
```
- **Example**: `GET /imoveis/referencia-PT00028/`
- **Description**: Directly locates a property by its business reference code (e.g. `PT00028`, `AP00163`) and returns the search card linking to the full property page.

### 3.4 Partial AJAX Results Fragment Endpoint

```http
GET /{search_path}/?pagina=resultado HTTP/1.1
Host: imobiliariavaleinvest.com.br
X-Requested-With: XMLHttpRequest
```
- **Example**: `GET /alugar/mg/coronel-fabriciano/?pagina=resultado`
- **Description**: Returns only the inner `#conteudo_resultado` HTML fragment containing the listing cards and pagination elements (33 KB instead of the full 80 KB page shell).

---

## 4. Request Parameters & Filter Behavior

All filters are encoded directly as path segments according to the Express router convention:

| Filter Type | Path Segment Pattern | Example | Description |
| :--- | :--- | :--- | :--- |
| **Transaction** | `/{finalidade}` | `/alugar`, `/comprar` | Rental vs. sale. |
| **State** | `/{uf}` | `/mg`, `/ba`, `/es` | Federal unit abbreviation. |
| **City** | `/{cidade}` | `/timoteo`, `/coronel-fabriciano` | Normalized municipality name. |
| **Neighborhood** | `/{bairro}` | `/centro`, `/funcionarios` | Normalized neighborhood name. |
| **Property Type** | `/{tipo}` | `/apartamento`, `/casa`, `/ponto` | Property typology. |
| **Subtype** | `/subtipo-{subtipo}` | `/subtipo-residencial` | Secondary typology classification. |
| **Bedrooms Exact** | `/dormitorios-{n}` | `/dormitorios-2` | Exact bedroom count. |
| **Bedrooms Min** | `/dormitorios-min_{n}` | `/dormitorios-min_2` | Minimum bedroom count. |
| **Bedrooms Range** | `/dormitorios-{min}_{max}` | `/dormitorios-2_4` | Bedroom interval. |
| **Bathrooms** | `/banheiros-{n}` | `/banheiros-1` | Bathroom count. |
| **Suites** | `/suites-{n}`, `/suites-min_{n}` | `/suites-1` | Suite count. |
| **Parking Spaces** | `/vagas-{n}`, `/vagas-min_{n}` | `/vagas-1` | Parking garage spaces. |
| **Price Interval** | `/valor-{min}_{max}` | `/valor-600_1500` | Price interval in BRL. |
| **Price Minimum** | `/valor-min_{min}` | `/valor-min_500` | Minimum rental price in BRL. |
| **Price Maximum** | `/valor-max_{max}` | `/valor-max_2000` | Maximum rental price in BRL. |
| **Built Area** | `/area-{min}_{max}`, `/area-min_{min}` | `/area-min_50` | Built area in square meters. |
| **Sorting** | `/ordem-{campo}/resultado-{dir}` | `/ordem-valor/resultado-crescente` | Order by `valor` or `recentes`. |
| **Page Size** | `/quantidade-{n}` | `/quantidade-12`, `/quantidade-24` | Items per page (default 12). |
| **Page Number** | `/pagina-{n}` | `/pagina-1`, `/pagina-2` | 1-indexed page number. |

---

## 5. Pagination & Boundary Behavior

- **Page Size**: **12 listings per page** by default. Custom page sizes (e.g. `24`) can be requested via `/quantidade-24/`.
- **Page Parameter**: `/pagina-{n}/` appended to the path (e.g. `/alugar/mg/coronel-fabriciano/pagina-2/`).
- **Total Count Element**: `<input id="countResultado" type="hidden" value="{total}"/>` contains the exact integer count of matching listings across all pages.
- **Pagination Navigation DOM**:
  - Container: `div.pagination ul.pagination`
  - Current page: `a.primary_color` (e.g. `1`)
  - Other page links: `a[href="javascript: paginacao('/alugar/.../pagina-{N}/');"]`
  - Next page button: `a.page-link` with text `»Próxima`
- **Boundary / Out-of-Bounds Behavior**:
  - Requesting an out-of-bounds page (e.g. `/alugar/pagina-99/`) returns `HTTP 200 OK` with `<input id="countResultado" type="hidden" value="36"/>` and `0` listing cards.
  - The client detects the end of pagination when the number of returned listing cards is `0`.

---

## 6. Search Results Card Parsing

Search result cards are rendered as anchor tags with class `.link_resultado`:

### 6.1 Card HTML Structure
```html
<a class="link_resultado" href="/alugar/mg/coronel-fabriciano/centro/ponto/78933085" target="_blank">
  <div class="resultado_novo">
    <div class="botao_favoritos_fundo" onclick="favoritos('78933085');">...</div>
    <div class="bloco_titulo">
      <h3 class="titulo_novo color2">PONTO</h3>
    </div>
    <div class="valor_novo">
      <small>LOCAÇÃO</small>
      <h5>R$ 620,00</h5>
    </div>
    <div class="foto_imovel">
      <div class="swiper swiper_resultados">
        <div class="swiper-wrapper">
          <div class="swiper-slide">
            <img src="https://cdn.uso.com.br/923136/2026/09/558bf6af0190777c8d0ddc75d4d2f3a7.jpg" />
          </div>
        </div>
      </div>
      <div class="icones_caracteristicas">
        <div class="detalhe_novo">
          <div class="icone_numero"><span>1</span></div>
          <span>banheiro</span>
        </div>
      </div>
    </div>
    <div class="final_card"><span>CENTRO - CORONEL FABRICIANO/MG</span></div>
    <div class="clicaveis_card">
      <div class="flag_ref color1"><span>Ref.PT00028</span></div>
    </div>
  </div>
</a>
```

### 6.2 Extraction Selectors
| Field | Selector / Extraction Logic | Example |
| :--- | :--- | :--- |
| **Property ID** | RegEx `/(\d+)/?$` on `a[href]` or `favoritos('...')` | `78933085` |
| **Reference Code** | `.flag_ref span` (remove `Ref.`) | `PT00028` |
| **Property Type** | `.titulo_novo` text | `PONTO` |
| **Transaction** | `.valor_novo small` text | `LOCAÇÃO` |
| **Rental Price** | `.valor_novo h5` text, converted to float | `620.0` (from `R$ 620,00`) |
| **Location** | `.final_card span` text | `CENTRO - CORONEL FABRICIANO/MG` |
| **Media / Photos** | `.swiper-slide img[src]` or `data-src` | `https://cdn.uso.com.br/923136/...` |
| **Amenities** | `.icones_caracteristicas .detalhe_novo` | `1 banheiro` |

---

## 7. Property Detail Retrieval

### 7.1 Detail Page Routing
```http
GET /{finalidade}/{uf}/{cidade}/{bairro}/{tipo}/{id} HTTP/1.1
Host: imobiliariavaleinvest.com.br
```
- **Example**: `GET /alugar/mg/coronel-fabriciano/centro/ponto/78933085`
- **Express Router Flexibility**: The router extracts `:id` as the final route parameter. Requests to `/alugar/a/b/c/d/78933085` or `/imoveis/a/b/c/d/78933085` resolve to the exact property detail page for ID `78933085`.

### 7.2 Detail Page Fields & Selectors
| Field | Selector / Element | Example Value |
| :--- | :--- | :--- |
| **Internal ID** | `input#pkimovel_ficha[value]` | `78933085` |
| **Agency ID** | `input#fkempresa_imovel_ficha[value]` | `923136` |
| **Reference Code** | `input#referencia_imovel_ficha[value]` | `PT00028` |
| **Agent ID** | `input#usuario_imovel_ficha[value]` | `337133` |
| **Title** | `h1.titulo` text | `Ponto Comercial para locação no Centro...` |
| **Location** | `h2.localizacao` text | `CENTRO - CORONEL FABRICIANO/MG` |
| **Rental Price** | `h4` text, converted to float | `620.0` (from `R$ 620,00`) |
| **Description** | `#descricao_imovel` text | Full textual description. |
| **Amenities** | `.detalhe_novo`, `.detalhes` | `1 sala, 1 banheiro, 11,00 m² de área` |
| **Photo Gallery** | `img.img-ficha.swiper_slide_img[data-src]` | High-resolution CDN images hosted on `cdn.uso.com.br`. |

---

## 8. Reproducibility & Verification Guide

### 8.1 Curl Verification Commands
```bash
# 1. User Target URL (timoteo, dormitorios-2, ordem-valor, crescente, quantidade-12)
curl -s -i "https://imobiliariavaleinvest.com.br/alugar/mg/timoteo/dormitorios-2/ordem-valor/resultado-crescente/quantidade-12/" | grep -E "countResultado|link_resultado"

# 2. Rental search with active listings (Coronel Fabriciano)
curl -s "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/" | grep -o 'class="link_resultado"' | wc -l

# 3. Property detail retrieval by ID
curl -s "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/78933085" | grep -E "pkimovel_ficha|referencia_imovel_ficha"

# 4. Taxonomy & inventory facets catalog
curl -s "https://imobiliariavaleinvest.com.br/data/localizacoes.json" | head -c 200
```

### 8.2 Python Client Verification Commands
```bash
# Execute standalone test suite
python3 scripts/run_tests.py

# Execute pytest suite
.venv/bin/pytest -v

# Run rental search CLI
python3 scripts/run_search.py --city "Coronel Fabriciano" --page-size 3

# View property details CLI
python3 scripts/run_property_detail.py 78933085
python3 scripts/run_property_detail.py PT00028

# Query taxonomy and inventory facets CLI
python3 scripts/run_facets.py
```
