# Data notice

## Source

The register data in this repository comes from the interim MiCA register of the European Securities and Markets Authority (ESMA), published as five CSV files on [ESMA's MiCA page](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica). The observatory republishes it in transformed form: as normalised weekly snapshots, a changelog, raw copies of the exports and CSV exports under `data/`, as the dashboard in the README, as `docs/feed.json`, `docs/changes.atom` and the digests under `digests/`, and as the figures in `editions/` and on the editions' HTML page (`docs/index.html`).

Source: ESMA, interim MiCA register.

## ESMA's legal notice

ESMA's legal notice is at <https://www.esma.europa.eu/legal-notice>, which redirects to <https://www.esma.europa.eu/about-esma/legal-notice-and-data-protection>. It was last retrieved on 14 November 2026 at 13:22 UTC; the copy is [`sources/esma/2026-11-14/legal-notice-and-data-protection.html`](sources/esma/2026-11-14/legal-notice-and-data-protection.html), SHA-256 `4345bbf28e134e3b47c26fdae63f198bafef06f6b648ce26e72b27e55163b7e8`. Its text is the same as in the first copy, retrieved on 14 October 2026 ([`sources/esma/2026-10-14/`](sources/esma/2026-10-14/legal-notice-and-data-protection.html)). It says:

> Reproduction of all information on this site (ESMA Library) is authorised except as otherwise stated, provided the source is acknowledged and:
>
> […]
>
> if the original material is transformed by the user (e.g. by making a summary of it or by translating it) and republished, this must be stated explicitly through the following disclaimer:
>
> - ‘This document has been drafted using material downloaded from ESMA’s website’ (or alternatively ‘This document constitutes a translation of a document downloaded from ESMA’s website’);
> - ESMA does not endorse this publication and in no way is liable for copyright or other intellectual property rights infringements nor for any damages caused to third parties through this publication’;

The observatory normalises, compares and counts the register rows and republishes the result. It treats the register files as ESMA material and every artefact derived from them as material "transformed by the user" and "republished". That reading is an interpretation, recorded in the [claim ledger](docs/regulatory-claim-ledger.md). It applies the disclaimer in ESMA's words:

**This document has been drafted using material downloaded from ESMA’s website. ESMA does not endorse this publication and in no way is liable for copyright or other intellectual property rights infringements nor for any damages caused to third parties through this publication.**

The disclaimer is stated in the README, in `docs/feed.json` (`notice`), in the generated data section of each edition and in the footer of the editions' HTML page. The files under `data/`, the digests and `docs/changes.atom` do not repeat it; this notice and the README cover them.

The legal notice sets further conditions. This repository is free of charge. It names ESMA as the source, with the disclaimer, in the places listed above, and each snapshot records the ESMA URL of every file it was built from. It marks the register data apart from its own analysis. It does not use ESMA's logo and implies no endorsement by ESMA of any firm, publication, product or service.

ESMA's MiCA page adds that the crypto-asset white papers listed in its register have not been reviewed or approved by any competent authority in any Member State of the European Union, and that the offeror and/or issuer of the crypto-asset is solely responsible for the content of each crypto-asset white paper. The observatory makes no assessment of any listed entity or white paper.

## What each licence covers

- **Code.** The MIT licence in [`LICENSE`](LICENSE) covers the code in this repository and reaches its documentation files, as its text says.
- **Prose.** The observatory's own prose in [`editions/`](editions/) and [`docs/`](docs/) is also licensed under the [Creative Commons Attribution 4.0 International licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/); reuse it under either licence. Under CC BY 4.0, attribute it to Sebastian Förste, MiCAR Register Observatory, with a link to this repository.
- **Data.** Neither licence extends to the register data in any form this repository republishes it, including the generated tables between the `data:start` and `data:end` markers of an edition, to text quoted from ESMA or from EU legal acts, or to the snapshots in [`sources/`](sources/).
- **Register data.** No licence is granted for the register data. Anyone who reuses it takes it under ESMA's terms quoted above.

The EU legal texts in [`sources/eu/`](sources/eu/) are copies retrieved from the Publications Office of the European Union. Their reuse terms are those of the Publications Office; this notice does not cover them.
