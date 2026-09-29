# Sector tag proposal for questions.yml

**Status: proposed, awaiting approval.** No tags are applied yet.

Tags only change question *order* (see `ordering.py`). Every SME still sees all 36 questions.

## How to read this

The ordering rule puts questions tagged with the selected sector first, universal (untagged) questions second, and questions tagged **only for other sectors** last. So each tag works both ways: it lifts a question for the sectors it names and **pushes it to the bottom for every other sector**. The proposal therefore tags sparingly, and only where one or more sectors have a clearly stronger reason to see a control early.

These tags are judgement calls based on typical sector risk profiles: guest Wi-Fi, patient data, operational technology (OT), staff turnover, invoice fraud. They are **not** derived from sector-level incident data. The csf-sme-coverage pipeline has no per-sector breakdown, and collecting one is out of scope.

## Proposed tags: 15 of 36 questions

| # | Question ID | Subcategory | Proposed `sectors` | Rationale |
|---|---|---|---|---|
| 3 | `least_privilege` | PR.AA-05 | healthcare, professional_services | Patient records and client-confidential files need tight access rights |
| 4 | `mfa_cloud_services` | PR.AA-05 | professional_services, ict | Heavy reliance on Microsoft 365, Google Workspace, Xero and similar SaaS |
| 6 | `network_segmentation` | PR.IR-01 | hospitality, retail, healthcare, education | Guest, customer, patient or student Wi-Fi shares premises with business systems |
| 7 | `vpn_remote` | PR.IR-01 | professional_services, ict | Remote and hybrid work is the norm |
| 10 | `wifi_password_strong` | PR.IR-01 | hospitality, retail | Wi-Fi is often set up by the ISP and never changed |
| 13 | `patching_firmware` | PR.PS-01 | manufacturing | Network and OT-adjacent devices are rarely updated |
| 16 | `mobile_device_managed` | DE.CM-09 | construction, healthcare | Site staff and clinicians work on phones and tablets |
| 17 | `backups_offline` | PR.DS-11 | healthcare, manufacturing | Ransomware downtime stops care or production |
| 19 | `backups_encrypted` | PR.DS-11 | healthcare, professional_services | Backups hold special-category or client-confidential data |
| 24 | `phishing_simulation` | PR.AT-01 | professional_services, construction | Frequent targets of invoice-redirection and business email compromise (BEC) fraud |
| 27 | `shadow_it_identified` | ID.AM-01 | ict, education | Staff (and students) adopt SaaS tools without review |
| 30 | `former_staff_disabled` | PR.AA-01 | hospitality, retail, construction | High turnover and seasonal or contract staff |
| 31 | `supplier_review` | GV.SC-04 | manufacturing, ict | Supply-chain and software-supplier dependency |
| 32 | `data_encryption` | PR.DS-01 | healthcare, professional_services, education | Laptops and USB drives carry patient, client or student data |
| 33 | `usb_policy` | PR.DS-01 | manufacturing, healthcare | USB transfer into OT machines and clinical devices |

The other **21 questions stay universal** (no tag). They cover MFA on email and admin accounts, firewall, admin interfaces, OS and app patching, endpoint protection, the remaining backups, policy, incident plan, training, asset inventory and owners, passwords, and all three logging questions.

## Tagged questions per sector

| Sector | Shown first | Question IDs |
|---|---|---|
| healthcare | 7 | least_privilege, network_segmentation, mobile_device_managed, backups_offline, backups_encrypted, data_encryption, usb_policy |
| professional_services | 6 | least_privilege, mfa_cloud_services, vpn_remote, backups_encrypted, phishing_simulation, data_encryption |
| manufacturing | 4 | patching_firmware, backups_offline, supplier_review, usb_policy |
| ict | 4 | mfa_cloud_services, vpn_remote, shadow_it_identified, supplier_review |
| retail | 3 | network_segmentation, wifi_password_strong, former_staff_disabled |
| hospitality | 3 | network_segmentation, wifi_password_strong, former_staff_disabled |
| construction | 3 | mobile_device_managed, phishing_simulation, former_staff_disabled |
| education | 3 | network_segmentation, shadow_it_identified, data_encryption |

## Trade-off to decide

For any given sector, 8–12 of the 15 tagged questions land in the bottom tier. Some of these belong to the highest-priority Subcategories. For example, `network_segmentation` (PR.IR-01, rank-1 combined score) would appear near the end for manufacturing, professional services, ICT and construction SMEs.

Options:
- **Accept it:** ordering is cosmetic and every question is still shown.
- **Tag less:** leave the top-priority PR.IR-01 and PR.AA-05 questions universal.
- **Change the rule:** show non-matching tagged questions in the universal tier (a two-tier ordering: matching first, then everything else in YAML order).
