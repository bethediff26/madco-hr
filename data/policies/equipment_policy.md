# Corporate Equipment and Hardware Policy

**Effective Date:** January 1, 2026  
**Last Revised:** September 1, 2026  
**Version:** 3.2  
**Approved By:** Chief Information Officer / VP of Human Resources  
**Department:** Information Technology — Asset Management  

---

## 1. Purpose

The Mad Company Corporate Equipment and Hardware Policy establishes the standards for provisioning, use, maintenance, refresh, return, and accountability of all company-issued technology equipment and hardware assigned to employees. This policy ensures consistent access to appropriate tools, extends device lifecycle management, protects corporate data assets, and defines clear expectations for both company-owned and personally-owned devices used for work purposes (BYOD). All employees receiving or managing company equipment must comply with the provisions herein.

---

## 2. Scope and Applicability

This policy applies to all full-time employees, part-time employees, temporary staff, and contractors who are issued company equipment or authorized to use personal devices for business purposes. It covers laptops, desktops, monitors, peripherals, mobile phones, tablets, networking hardware, and any other technology assets procured or subsidized by Mad Company.

---

## 3. Company Laptop Allocation Standards

### 3.1 Standard Device Tiers

Employees are allocated laptop devices based on their role category and technical requirements:

| Role Category | Standard Device | Rationale |
|---|---|---|
| Individual Contributor (IC) — General | Business-class ultrabook (e.g., Dell Latitude or equivalent) with 16 GB RAM, 512 GB SSD | Standard productivity workloads, video conferencing, document creation |
| Individual Contributor — Technical (Engineering, Data Science) | Performance workstation (e.g., Dell Precision or MacBook Pro) with 32 GB RAM, 1 TB SSD | Development environments, local builds, data processing |
| Manager / Director | Business-class ultrabook with enhanced security features (TPM 2.0, biometric authentication) | Standard productivity with elevated security posture |
| Executive / C-Suite | Premium workstation with extended warranty and priority support | Executive mobility requirements, extended battery life, premium peripherals |
| Design / Creative | Color-accurate display workstation (e.g., MacBook Pro or Dell XPS with calibrated 4K monitor) | Graphic design, video editing, creative production |

### 3.2 Peripheral Allocation

Each employee receives one external monitor (27-inch, 1440p minimum), an ergonomic keyboard and mouse, and a USB-C docking station. Additional peripherals (webcams, headsets, secondary monitors) require manager approval and must be justified by documented role requirements.

### 3.3 Mobile Phone Allocation

Employees whose roles require regular off-site communication or field access are eligible for a company-issued mobile device. Standard allocations include the latest iPhone or Android enterprise model with a managed mobile plan. Employees in non-field-facing roles may request a phone through the IT procurement process, subject to budget availability and VP approval.

---

## 4. Device Refresh Cycle

### 4.1 Three-Year Standard Refresh

All company-issued laptops and desktops follow a **three-year (36-month) refresh cycle** from the date of initial deployment. At the end of each device's lifecycle, IT Asset Management issues a replacement unit with current-generation specifications matching the employee's role tier. The old device is collected, sanitized per NIST 800-88 guidelines, and either redeployed to a lower-tier role or responsibly recycled through an e-waste certified vendor.

### 4.2 Early Replacement Criteria

Devices may be replaced before their scheduled refresh date under the following conditions:
- **Hardware Failure:** The device has been diagnosed by IT Support as having a non-warranty-repairable fault or recurring hardware issues exceeding $300 in cumulative repair costs within a twelve-month period.
- **Performance Degradation:** The device no longer meets the minimum performance requirements for the employee's role, as documented by IT and confirmed by the manager.
- **Security Non-Compliance:** The device cannot support current security standards (e.g., TPM 2.0, Secure Boot) despite available firmware updates.

Early replacement requests require submission of an IT Service Ticket with supporting documentation and manager approval.

### 4.3 Extended Use Exceptions

Employees may request to retain their current device beyond the three-year cycle for up to twelve additional months under exceptional circumstances (e.g., specialized software compatibility, custom configurations). Such extensions require written justification from the employee's manager and IT Security approval confirming no security risk.

---

## 5. BYOD (Bring Your Own Device) MDM Setup

### 5.1 BYOD Eligibility

Employees may use personally-owned devices for work purposes only if:
- Their role does not require specialized hardware that the company must provide.
- The device meets minimum security and compatibility standards defined by IT Security.
- The employee voluntarily consents to Mobile Device Management (MDM) enrollment.
- A signed BYOD Acceptable Use Agreement is on file in Workday.

### 5.2 MDM Enrollment Requirements

All BYOD devices must be enrolled in the company's MDM platform (Microsoft Intune) and maintain the following security posture:
- Operating system at the latest stable release or within one minor version of the current release.
- Full-disk encryption enabled and active.
- Screen lock with passcode (minimum 6 digits or alphanumeric, minimum 8 characters).
- Company-approved endpoint protection agent installed and reporting status.
- Jailbroken or rooted devices are **prohibited** from BYOD enrollment.

### 5.3 BYOD Data Separation

The MDM profile creates a secure container on the device that isolates corporate data from personal data. IT Security retains the ability to remotely wipe only the corporate container — never personal data — upon separation of employment or device loss. Employees are notified before any remote wipe action is executed.

### 5.4 BYOD Reimbursement

Employees using approved BYOD devices receive a **$30 monthly technology stipend** toward their phone and data plan costs. This stipend is processed as a payroll supplement and requires annual verification that the device continues to meet MDM security standards.

---

## 6. Device Loss, Theft, and Damage Protocols

### 6.1 Lost or Stolen Devices

If a company-issued or BYOD device is lost or stolen, the employee must:
1. Report the incident to IT Security at **security@madcompany.com** and call the IT Emergency Hotline at **(555) 0199** within **one (1) hour** of discovery.
2. Initiate a remote lock or wipe via the MDM console immediately upon notification.
3. File a police report if theft is suspected, obtaining a case number for insurance purposes.
4. Submit an Incident Report through Workday's HR Case Management module within **twenty-four (24) hours**.

### 6.2 Accidental Damage

Employees who accidentally damage a company device must report the incident to IT Helpdesk within **forty-eight (48) hours**. Repair or replacement costs may be deducted from the employee's paycheck only if negligence is documented and approved by HR in accordance with applicable state wage-and-hour laws. Normal wear and tear is never charged to the employee.

### 6.3 Insurance Coverage

Mad Company maintains a corporate insurance policy covering theft and accidental damage of company-issued equipment up to $2,000 per incident. Employees are not required to pay deductibles for covered losses attributable to normal business activities.

---

## 7. Hardware Return Policy Upon Offboarding

### 7.1 Return Timeline

All company-issued equipment must be returned to IT Asset Management within **five (5) business days** of an employee's separation date (voluntary resignation, involuntary termination, or layoff). Remote employees receive a prepaid shipping label and packaging kit mailed to their address upon receipt of separation confirmation.

### 7.2 Return Checklist

Returned items must include:
- Laptop or desktop unit with original charger and power cable.
- All issued peripherals (monitors, keyboard, mouse, docking station).
- Mobile device with carrier SIM card (if applicable).
- Access badges, security tokens, and physical keys.
- Any documentation or materials bearing company markings.

### 7.3 Data Sanitization

Upon receipt of returned equipment, IT Asset Management performs a full data sanitization per NIST 800-88 Rev. 4 standards. Devices are verified clean before any redeployment or recycling. The sanitization process is logged and retained for audit purposes.

### 7.4 Failure to Return Equipment

Employees who fail to return company equipment within the specified timeframe may have their final paycheck (to the extent permitted by law), expense reimbursements, or COBRA premiums withheld to offset the cost of unrecovered assets. Persistent non-return may result in civil action for conversion of company property. The company reserves the right to report stolen equipment to local law enforcement.

---

## 8. Equipment Maintenance and Repair

### 8.1 Warranty Coverage

All company-issued devices are covered by manufacturer warranties extended through a corporate service contract providing next-business-day on-site repair for hardware failures. Employees must not attempt self-repair or use unauthorized third-party repair services, as this may void warranty coverage.

### 8.2 Software Updates and Patches

Employees are required to install all critical security patches and operating system updates within **seven (7) calendar days** of availability. IT deploys non-critical updates during scheduled maintenance windows communicated biweekly via the IT newsletter. Failure to maintain an up-to-date device may result in temporary suspension of network access until compliance is restored.

---

## Revision History

| Version | Date | Changes | Approved By |
|---|---|---|---|
| 3.0 | January 1, 2025 | Introduced three-year refresh cycle; added BYOD MDM provisions | CIO / VP HR |
| 3.1 | May 15, 2026 | Added role-based device tier table; clarified early replacement criteria | IT Director / Legal |
| 3.2 | September 1, 2026 | Updated BYOD stipend to $30/month; added insurance coverage details | CIO / Finance / VP HR |

---

## Department Contacts

**IT Asset Management**  
Email: itassets@madcompany.com  
Phone: (555) 0199 ext. 5100  
Office: Building B, Suite 100, Mon–Fri 8:00 AM – 6:00 PM EST

**IT Helpdesk — Equipment Support**  
Email: helpdesk@madcompany.com  
Phone: (555) 0199 (24/7)

---

*This document is the property of Mad Company Corporation. Unauthorized reproduction or distribution is prohibited.*
