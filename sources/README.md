# Source snapshots

Byte-exact copies of the primary sources that the README, the data notice, the regulatory claim ledger and the source monitor rely on. Each file is stored exactly as it was served. Never edit a snapshot by hand: when a source changes, retrieve it again, add the new file next to the old one and record it below.

Legal texts come from the Publications Office of the European Union, requested with `Accept: application/xhtml+xml` and `Accept-Language: eng`:

```bash
curl -sSL -H "Accept: application/xhtml+xml" -H "Accept-Language: eng" \
  https://publications.europa.eu/resource/celex/<CELEX>
```

ESMA pages and files come from `www.esma.europa.eu` with the observatory's user agent. SHA-256 is computed over the stored bytes.

## EU legal texts

First retrieved on 14 October 2026 between 10:08 and 10:09 UTC. Retrieved again on 14 November 2026 at 13:21 UTC from the same URLs: each of the six texts was served from the same Cellar manifestation with the same SHA-256, so the stored copies are unchanged. The corrigendum was retrieved on 14 November 2026.

| File | Instrument | Requested | Served from | SHA-256 | Bytes | Relied on for |
| --- | --- | --- | --- | --- | ---: | --- |
| [`eu/32023R1114.xhtml`](eu/32023R1114.xhtml) | Regulation (EU) 2023/1114 (MiCAR), OJ L 150, 9.6.2023, p. 40 | `https://publications.europa.eu/resource/celex/32023R1114` | `http://publications.europa.eu/resource/cellar/01d55833-0660-11ee-b12e-01aa75ed71a1.0006.03/DOC_1` | `c694819af2efbd715735cacf4bb65eade4685f88b30787197658122ff04c26fb` | 1681465 | Art. 3(1)(16), 6(10), 19(9), 51(9), 109(1), (3)(c), (4)(c) and (8), 110(1) to (3) |
| [`eu/02023R1114-20240109.xhtml`](eu/02023R1114-20240109.xhtml) | MiCAR, consolidated text as at 9 January 2024 (documentation only, no legal effect) | `https://publications.europa.eu/resource/celex/02023R1114-20240109` | `http://publications.europa.eu/resource/cellar/92d9c8a8-b47a-11ee-b164-01aa75ed71a1.0006.02/DOC_2` | `078da6ed766fe117be60ff63536f25101ec21f2dec175394eef7bf82c02ffe19` | 1188920 | Art. 110a, marked ►M1 (Regulation (EU) 2023/2869); Art. 109 and 110 identical to the OJ text |
| [`eu/32023R1114R03.xhtml`](eu/32023R1114R03.xhtml) | Corrigendum to Regulation (EU) 2023/1114, CELEX `32023R1114R(03)`, OJ L, 2024/90275, 2.5.2024 (English) | `https://publications.europa.eu/resource/celex/32023R1114R%2803%29` | same | `6b058e7b7e86924defd562a997fc1ac266bda4eb9f81ccee84740c259fcfde2d` | 17345 | It corrects Art. 45(4), 81(15), 92(2) and 111(1) only, none of the provisions cited here |
| [`eu/32023R2869.xhtml`](eu/32023R2869.xhtml) | Regulation (EU) 2023/2869 (ESAP amendments), OJ L, 2023/2869, 20.12.2023 | `https://publications.europa.eu/resource/celex/32023R2869` | `http://publications.europa.eu/resource/cellar/e934cc57-9ed8-11ee-b164-01aa75ed71a1.0006.03/DOC_1` | `014f594e7d4994c7abc1d6375fc6c8c313a6066a55c9054e82857a77387fb3fd` | 330005 | Art. 18, which inserts Art. 110a into MiCAR |
| [`eu/32023R2859.xhtml`](eu/32023R2859.xhtml) | Regulation (EU) 2023/2859 (ESAP), OJ L, 2023/2859, 20.12.2023 | `https://publications.europa.eu/resource/celex/32023R2859` | `http://publications.europa.eu/resource/cellar/e3cb73db-9ed8-11ee-b164-01aa75ed71a1.0006.03/DOC_1` | `c2e4cd75ea1ff61abc04ee37f8bb2867b4e765c0c3377d269e53747a51122754` | 225789 | Art. 2, points (3) and (4), the definitions Art. 110a cross-refers to |
| [`eu/32025R0421.xhtml`](eu/32025R0421.xhtml) | Commission Delegated Regulation (EU) 2025/421, OJ L, 2025/421, 24.3.2025 | `https://publications.europa.eu/resource/celex/32025R0421` | `http://publications.europa.eu/resource/cellar/3034df96-0851-11f0-b1a3-01aa75ed71a1.0006.03/DOC_1` | `1bccd4f61141d914960bd024c539088363aa217cfd5ae7f7f75515e1d299d4f2` | 63313 | Title, legal basis (Art. 109(8), third subparagraph, MiCAR), Art. 1 and Art. 4 (applies from 23 December 2025) |
| [`eu/32024R2984.xhtml`](eu/32024R2984.xhtml) | Commission Implementing Regulation (EU) 2024/2984, OJ L, 2024/2984, 3.12.2024 | `https://publications.europa.eu/resource/celex/32024R2984` | `http://publications.europa.eu/resource/cellar/6e4786f3-b117-11ef-acb1-01aa75ed71a1.0006.03/DOC_1` | `f1b7d169de7bc7b96814b570b8de6eec7cc67445bc51d68bde578bbd44f2afb5` | 390428 | Art. 2(1) (XHTML with Inline XBRL), Art. 4, second paragraph (applies from 23 December 2025), and recital 5 (aim of the XBRL mark-up, cited in the Q3 edition) |

**Amendment check.** The Publications Office SPARQL endpoint (`https://publications.europa.eu/webapi/rdf/sparql`) was asked on 14 October 2026 and again on 14 November 2026 which acts amend or correct the instruments above. Both times it listed:

- for MiCAR, two consolidated versions, `02023R1114-20230609` and `02023R1114-20240109`, and one amending act, `32023R2869` of 13 December 2023;
- for MiCAR, six corrigenda, `32023R1114R(01)` to `R(06)`. Only `R(03)` is available in English; it is stored above and changes none of the cited provisions. The other five returned HTTP 404 for an English request on 14 November 2026;
- for Regulation (EU) 2023/2859, the amending acts `32024L1760` and `32024R3005`, which add entries to its Annex only (read on 14 November 2026; they are not stored because nothing here relies on them), and the corrigendum `32023R2859R(01)`, which has no English version;
- for Regulations (EU) 2023/2869, 2024/2984 and 2025/421, no amending act and no corrigendum.

## ESMA

### 14 November 2026

Retrieved with the observatory's user agent; the time is the server's `Date` header.

| File | Requested | Served from | Retrieved (UTC) | SHA-256 | Bytes | Relied on for |
| --- | --- | --- | --- | --- | ---: | --- |
| [`esma/2026-11-14/legal-notice-and-data-protection.html`](esma/2026-11-14/legal-notice-and-data-protection.html) | `https://www.esma.europa.eu/legal-notice` | `https://www.esma.europa.eu/about-esma/legal-notice-and-data-protection` (301 redirect) | 13:22:08 | `4345bbf28e134e3b47c26fdae63f198bafef06f6b648ce26e72b27e55163b7e8` | 101606 | The quoted wording in [`DATA_NOTICE.md`](../DATA_NOTICE.md). The page's text is the same as on 14 October 2026; only markup bytes differ |
| [`esma/2026-11-14/markets-crypto-assets-regulation-mica.html`](esma/2026-11-14/markets-crypto-assets-regulation-mica.html) | `https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica` | same | 13:22:09 | `efb720acff4e75aa6fce7d9d68f1a328956ee81b082c07fd47562e8c9386be3c` | 90293 | "Last update: 11 November 2026"; the five register CSV links and the field description link the source monitor reads, unchanged since 14 October 2026, plus a new link to a MIDAS feedback sample CSV; the statement that the interim register is a collection of CSV files "until mid-2026" |
| [`esma/2026-11-14/Description_of_the_fields_in_the_interim_MiCA_register.csv`](esma/2026-11-14/Description_of_the_fields_in_the_interim_MiCA_register.csv) | `https://www.esma.europa.eu/sites/default/files/2024-12/Description_of_the_fields_in_the_interim_MiCA_register.csv` | same | 13:22:09 | `2e0b84450f01bda55dc2da6dd842094fb413e74694a655b94a3d7f79faf504b1` | 14292 | Field lists per file, including the CASP field `ac_legal_basis` marked "NEW - as of Oct 2026"; the placeholder values `EMT_NO_WP` and `EMT_CRIN` of `EMTWP.csv` (`Last-Modified` 5 November 2026) |

### 14 October 2026

| File | Requested | Served from | Retrieved (UTC) | SHA-256 | Bytes | Relied on for |
| --- | --- | --- | --- | --- | ---: | --- |
| [`esma/2026-10-14/legal-notice-and-data-protection.html`](esma/2026-10-14/legal-notice-and-data-protection.html) | `https://www.esma.europa.eu/legal-notice` | `https://www.esma.europa.eu/about-esma/legal-notice-and-data-protection` (301 redirect) | 10:09:26 | `53e1038606d7a6dee7ce65509d216ac8100affcc1cbed186e9eed2cb5cb2e95f` | 101484 | The first reading of the legal notice |
| [`esma/2026-10-14/markets-crypto-assets-regulation-mica.html`](esma/2026-10-14/markets-crypto-assets-regulation-mica.html) | `https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica` | same | 10:09:53 | `90f7e23ade5f294d516b49923b3407d3fe65664cf3a354acef969ef4b63a74e1` | 88571 | "Last update: 7 October 2026" and the six CSV links of that day |
| [`esma/2026-10-14/Description_of_the_fields_in_the_interim_MiCA_register.csv`](esma/2026-10-14/Description_of_the_fields_in_the_interim_MiCA_register.csv) | `https://www.esma.europa.eu/sites/default/files/2024-12/Description_of_the_fields_in_the_interim_MiCA_register.csv` | same | 10:10:13 | `7d89b5d4ff83ccf07bb2673e864def28dfed410eef5add3a2c5a623ceb8ad295` | 13968 | The field lists before `ac_legal_basis` was added |

## ESMA interim register files: header rows observed

Retrieved on 14 November 2026 at 13:23 UTC from `https://www.esma.europa.eu/sites/default/files/2024-12/<file>`. The file bodies are not stored here: they hold register rows, which the weekly refresh keeps under `data/raw/`. Every file was served with HTTP 200 and `Content-Type: text/csv`, without a charset parameter, and starts with a UTF-8 byte order mark. `Last-Modified` was 11 November 2026 for every file except `ARTZZ.csv` (14 February 2025). The non-empty names of each header row, in order, are the schema the source monitor expects (`columns` in `src/observatory/config.py`).

| File | SHA-256 of the body | Bytes | Data rows | Header row |
| --- | --- | ---: | ---: | --- |
| `OTHER.csv` | `bd9b22a03d4ade4442757d01ffa81859bd9235a998476f0388653b2136a8bd36` | 254839 | 1077 | `ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei,ae_lei_cou_code,ae_lei_name_casp,ae_lei_casp,ae_offerCode_cou,ae_DTI_FFG,ae_DTI,wp_url,wp_comments,wp_lastupdate` |
| `EMTWP.csv` | `53dfa4ee351a70b91be80b2e3ecb086268df262e388b0d0c4d42665959e434f4` | 18252 | 51 | `ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei,ae_lei_cou_code,ae_commercial_name,ae_address,ae_website,ac_authorisationNotificationDate,ac_authorisationEndDate,ae_exemption48_4,ae_exemption48_5,ae_authorisation_other_emt,ae_DTI_FFG,ae_DTI,wp_url,wp_authorisationNotificationDate,wp_comments,wp_lastupdate` |
| `ARTZZ.csv` | `fa1ef4da123e3d49642c69f90a81a88f6c2cc2a0b9471b2108e4dfc635ca7c67` | 276 | 0 | `ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei,ae_lei_cou_code,ae_commercial_name,ae_address,ae_website,ac_authorisationNotificationDate,ac_authorisationEndDate,ae_credit_institution,wp_url,wp_authorisationNotificationDate,wp_url_cou,wp_comments,wp_lastupdate` |
| `CASPS.csv` | `e0a73cab442a1bedf84a9fbfe756f7a2779bf48050c4d147c4971788d4279be3` | 201399 | 407 | `ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei,ae_lei_cou_code,ae_commercial_name,ae_address,ae_website,ae_website_platform,ac_authorisationNotificationDate,ac_authorisationEndDate,ac_serviceCode,ac_serviceCode_cou,ac_comments,ac_lastupdate,ac_legal_basis,` |
| `NCASP.csv` | `7ef652213f2982e34b8b7e5a194c5dd2ee9edf01ebe1d610db863536d1f5729c` | 38783 | 216 | `ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei,ae_lei_cou_code,ae_commercial_name,ae_website,ae_infrigment,ae_reason,ae_decision_date,ae_comments,ae_lastupdate` |

Data rows are the non-blank rows after the header, without repeated header lines. Differences from ESMA's field description file of 14 November 2026:

- `CASPS.csv` ends its header with a comma, so it has a trailing column without a name (two on 9 November 2026). The monitor ignores nameless columns.
- `CASPS.csv` carries `ac_legal_basis` from the export recorded on 19 October 2026 on; the 14 October field description did not list it, the 14 November one does.
- `ARTZZ.csv` lacks the `ae_DTI_FFG` and `ae_DTI` columns that the description lists for it.
- `NCASP.csv` spells `ae_infrigment` as the description does.
