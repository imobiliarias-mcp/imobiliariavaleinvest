# Grupo Union Real Estate Platform API Specification — Imobiliária Vale Invest

## 1. Overview & Architecture

This document serves as the **Single Source of Truth (SOT)** for the reverse-engineered rental search and property management APIs powering **Imobiliária Vale Invest** (`https://imobiliariavaleinvest.com.br/`).

### 1.1 Platform Identification
- **SaaS Vendor**: [Grupo Union / USO](https://www.uso.com.br/) (Union Softwares / BuscaImo / Praedium)
- **Backend Architecture**: Node.js / Express web server behind OpenResty (Nginx) reverse proxy
- **Frontend Frameworks**: Semantic UI, Leaflet, Swiper
- **Character Encoding**: `text/html; charset=utf-8`
- **Asset / Media CDN**:
  - `https://cdn.uso.com.br/`
  - `https://cdn2.uso.com.br/`
  - `https://cdn5.uso.com.br/`
  - `https://grupo-union.s3.amazonaws.com/`

### 1.2 Authentication & Access Control
- **Authentication**: None required.
- **Statelessness**: Fully stateless queries. Cookies issued by Express are not required for reproduction.
- **Mandatory Headers**: Standard desktop `User-Agent`.

---

## 2. Endpoints Catalog

### 2.1 Property Search & Listings
- **URL**: `GET https://imobiliariavaleinvest.com.br/{finalidade}/{uf}/{cidade}/{bairro}/{tipo}/{specs}/`
- **Headers**: `User-Agent`
- **Path Parameters**:
  - `finalidade`: `alugar` (default), `comprar`, `comprar-ou-alugar`
  - `uf`: `mg`
  - `cidade`: `timoteo`, `coronel-fabriciano`, `ipatinga`
  - `bairro`: `centro`, `funcionarios`, `floresta`
  - `tipo`: `apartamento`, `casa`, `ponto`, `sala`, `galpao`, `terreno`, `lote`
  - `dormitorios`: `dormitorios-{n}`, `dormitorios-min_{n}`, `dormitorios-{min}_{max}`
  - `valor`: `valor-{min}_{max}`, `valor-min_{min}`, `valor-max_{max}`
  - `ordem`: `ordem-{campo}/resultado-{direcao}` (`ordem-valor/resultado-crescente`)
  - `quantidade`: `quantidade-{n}` (default 12)
  - `pagina`: `pagina-{n}` (1-indexed)

### 2.2 Property Detail Retrieval
- **URL**: `GET https://imobiliariavaleinvest.com.br/{finalidade}/{uf}/{cidade}/{bairro}/{tipo}/{id}`
- **Route Matcher**: `/:finalidade/:uf/:cidade/:bairro/:tipo/:id` (or `/:finalidade/*/*/*/*/:id`)
- **Key Page Attributes**:
  - `input#pkimovel_ficha[value]`: Internal integer ID
  - `input#referencia_imovel_ficha[value]`: Business reference code
  - `h1.titulo`: Full title
  - `h2.localizacao`: Municipality and neighborhood
  - `h4`: Rental price
  - `#descricao_imovel`: Full description text
  - `img.swiper_slide_img[data-src]`: Full-resolution photos

### 2.3 Taxonomy & Inventory Facet Catalog
- **URL**: `GET https://imobiliariavaleinvest.com.br/data/localizacoes.json`
- **Response**: Array containing `imoveis` catalog with 400 entries.

### 2.4 Reference Code Direct Lookup
- **URL**: `GET https://imobiliariavaleinvest.com.br/imoveis/referencia-{ref}/`
- **Response**: HTML search card pointing directly to canonical property page.
