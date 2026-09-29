# Sector tag proposal for questions.yml

**Status: approved and applied**, with the three-tier ordering rule kept. After review, three tags were refined (see [Revisions](#revisions)). The tables below match `questions.yml`.

Tags only change question *order* (see `ordering.py`). Every SME still sees all 36 questions.

## How to read this

The ordering rule puts questions tagged with the selected sector first, universal (untagged) questions second, and questions tagged **only for other sectors** last. So each tag works both ways: it lifts a question for the sectors it names and **pushes it to the bottom for every other sector**. The proposal therefore tags sparingly, and only where one or more sectors have a clearly stronger reason to see a control early.

These tags are judgement calls based on typical sector risk profiles: guest Wi-Fi, patient data, operational technology (OT), staff turnover, invoice fraud. The `phishing_simulation` revision also draws on the industry-level social-engineering patterns reported in the Verizon DBIR. The tags are **not** computed from sector-level data: the csf-sme-coverage pipeline has no per-sector breakdown, and collecting one is out of scope.

## Tags: 15 of 36 questions

| # | Question ID | Subcategory | `sectors` | Rationale |
|---|---|---|---|---|
| 3 | `least_privilege` | PR.AA-05 | healthcare, professional_services | Patient records and client-confidential files need tight access rights |
| 4 | `mfa_cloud_services` | PR.AA-05 | professional_services, ict | Heavy reliance on Microsoft 365, Google Workspace, Xero and similar SaaS |
| 6 | `network_segmentation` | PR.IR-01 | hospitality, retail, healthcare, education | Guest, customer, patient or student Wi-Fi shares premises with business systems |
| 7 | `vpn_remote` | PR.IR-01 | professional_services, ict | Remote and hybrid work is the norm |
| 10 | `wifi_password_strong` | PR.IR-01 | hospitality, retail | Wi-Fi is often set up by the ISP and never changed |
| 13 | `patching_firmware` | PR.PS-01 | manufacturing, construction | Network, OT-adjacent and site IoT devices (cameras, telematics, equipment monitoring) are rarely updated |
| 16 | `mobile_device_managed` | DE.CM-09 | construction, healthcare, hospitality | Site staff and clinicians work on phones and tablets; hospitality runs shared tablets, tills and guest-facing devices |
| 17 | `backups_offline` | PR.DS-11 | healthcare, manufacturing | Ransomware downtime stops care or production |
| 19 | `backups_encrypted` | PR.DS-11 | healthcare, professional_services | Backups hold special-category or client-confidential data |
| 24 | `phishing_simulation` | PR.AT-01 | professional_services, healthcare, hospitality | Professional services: invoice-redirection and business email compromise (BEC) fraud. Healthcare and hospitality: higher social-engineering exposure reported in the DBIR |
| 27 | `shadow_it_identified` | ID.AM-01 | ict, education | Staff (and students) adopt SaaS tools without review |
| 30 | `former_staff_disabled` | PR.AA-01 | hospitality, retail, construction | High turnover and seasonal or contract staff |
| 31 | `supplier_review` | GV.SC-04 | manufacturing, ict | Supply-chain and software-supplier dependency |
| 32 | `data_encryption` | PR.DS-01 | healthcare, professional_services, education | Laptops and USB drives carry patient, client or student data |
| 33 | `usb_policy` | PR.DS-01 | manufacturing, healthcare | USB transfer into OT machines and clinical devices |

The other **21 questions stay universal** (no tag). They cover MFA on email and admin accounts, firewall, admin interfaces, OS and app patching, endpoint protection, the remaining backups, policy, incident plan, training, asset inventory and owners, passwords, and all three logging questions.

## Tagged questions per sector

| Sector | Shown first | Question IDs |
|---|---|---|
| healthcare | 8 | least_privilege, network_segmentation, mobile_device_managed, backups_offline, backups_encrypted, phishing_simulation, data_encryption, usb_policy |
| professional_services | 6 | least_privilege, mfa_cloud_services, vpn_remote, backups_encrypted, phishing_simulation, data_encryption |
| manufacturing | 4 | patching_firmware, backups_offline, supplier_review, usb_policy |
| ict | 4 | mfa_cloud_services, vpn_remote, shadow_it_identified, supplier_review |
| retail | 3 | network_segmentation, wifi_password_strong, former_staff_disabled |
| hospitality | 5 | network_segmentation, wifi_password_strong, mobile_device_managed, phishing_simulation, former_staff_disabled |
| construction | 3 | patching_firmware, mobile_device_managed, former_staff_disabled |
| education | 3 | network_segmentation, shadow_it_identified, data_encryption |

## Trade-off (accepted)

For any given sector, 7–12 of the 15 tagged questions land in the bottom tier. Some of these belong to the highest-priority Subcategories. For example, `network_segmentation` (PR.IR-01, rank-1 combined score) would appear near the end for manufacturing, professional services, ICT and construction SMEs.

This was accepted: ordering is cosmetic and every question is still shown. The alternatives were to leave the top-priority PR.IR-01 and PR.AA-05 questions universal, or to use two tiers (matching first, then everything else in YAML order).

## Revisions

| Question | Original | Revised | Change |
|---|---|---|---|
| `phishing_simulation` | professional_services, construction | professional_services, healthcare, hospitality | Dropped construction; added healthcare and hospitality |
| `mobile_device_managed` | construction, healthcare | construction, healthcare, hospitality | Added hospitality |
| `patching_firmware` | manufacturing | manufacturing, construction | Added construction |

Net effect: healthcare 7 → 8, hospitality 3 → 5, construction unchanged at 3 (lost `phishing_simulation`, gained `patching_firmware`).
