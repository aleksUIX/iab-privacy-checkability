# 2.7 Privacy

## 2.7 - Privacy <a name="privacy"></a>

Without limiting the scope of the Disclaimer, the OpenRTB specification does include several features to support implementer’s communication of information regarding consumer privacy, including, but not limited to:

- The status of do not track headers (Section 3.2.18)
- Presence of site/app privacy policies (Section 3.2.13 and Section 3.2.14)
- Regulations or laws that the transmitter of a bid request believes are applicable (Section 3.2.3)
- Consent and opt-out information strings for the user (Global Privacy Platform, US Privacy String and Transparency and Consent Framework consent strings) (Section 3.2.3 and Section 3.2.20)

As noted in the Disclaimer, each implementer is responsible to ensure that their implementation complies with any applicable laws, regulations, or self-regulatory frameworks.



# 3.2.3 Regs

### 3.2.3 - Object: Regs <a name="objectregs"></a>

This object contains any legal, governmental, or industry regulations that the sender deems applicable to the request. See Section 7.5 for more details on the flags supporting Coppa, GDPR and others.

| Attribute | Type | Description |
| --- | --- | --- |
| `coppa` | integer | Flag indicating if this request is subject to the COPPA regulations established by the USA FTC, where 0 = no, 1 = yes. Refer to Section 7.5 for more information. |
| `gdpr` | integer | Flag that indicates whether or not the request is subject to GDPR regulations 0 = No, 1 = Yes, omission indicates unknown. Refer to Section 7.5 for more information. |
| `us_privacy` | string | Communicates signals regarding consumer privacy under US privacy regulation. See [US Privacy String specifications](https://github.com/InteractiveAdvertisingBureau/USPrivacy/blob/master/CCPA/US%20Privacy%20String.md). Refer to Section 7.5 for more information. |
| `gpp` | string | Contains the Global Privacy Platform’s consent string. See the [Global Privacy Platform specification](https://github.com/InteractiveAdvertisingBureau/Global-Privacy-Platform) for more details. |
| `gpp_sid` | integer array | Array of the section(s) of the string which should be applied for this transaction. Generally will contain one and only one value, but there are edge cases where more than one may apply. GPP Section 3 (Header) and 4 (Signal Integrity) do not need to be included. See the [GPP Section Information](https://github.com/InteractiveAdvertisingBureau/Global-Privacy-Platform/blob/main/Sections/Section%20Information.md) for more details. |
| `ext` | object | Placeholder for exchange-specific extensions to OpenRTB. |




# 3.2.18 Device

### 3.2.18 - Object: Device <a name="objectdevice"></a>

This object provides information pertaining to the device through which the user is interacting. Device information includes its hardware, platform, location, and carrier data. The device can refer to a mobile handset, a desktop computer, set top box, or other digital device.

| Attribute | Type | Description |
| --- | --- | --- |
| `geo` | object; recommended | Location of the device assumed to be the user’s current location defined by a `Geo` object (Section 3.2.19). |
| `dnt` | integer; recommended | Standard “Do Not Track” flag as set in the header by the browser, where 0 = tracking is unrestricted, 1 = do not track. |
| `lmt` | integer; recommended | “Limit Ad Tracking” signal commercially endorsed (e.g., iOS, Android), where 0 = tracking is unrestricted, 1 = tracking must be limited per commercial guidelines. |
| `ua` | string | Browser user agent string. This field represents a raw user agent string from the browser. For backwards compatibility, exchanges are recommended to always populate `ua` with the User-Agent string, when available from the end user’s device, even if an alternative representation, such as the User-Agent Client-Hints, is available and is used to populate `sua`. No inferred or approximated user agents are expected in this field.<br>If a client supports User-Agent Client Hints, and `sua` field is present, bidders are recommended to rely on `sua` for detecting device type, browser type and version and other purposes that rely on the user agent information, and ignore `ua` field. This is because the `ua` may contain a frozen or reduced user agent string. |
| `sua` | object | Structured user agent information defined by a `UserAgent` object (see Section 3.2.29). If both `ua` and `sua` are present in the bid request, `sua` should be considered the more accurate representation of the device attributes. This is because the `ua` may contain a frozen or reduced user agent string. |
| `ip` | string | IPv4 address closest to device. |
| `ipv6` | string | IP address closest to device as IPv6. |
| `devicetype` | integer | The general type of device. Refer to [List: Device Types](https://github.com/InteractiveAdvertisingBureau/AdCOM/blob/master/AdCOM%20v1.0%20FINAL.md#list--device-types-) in AdCOM 1.0. |
| `make` | string | Device make (e.g., “Apple”). |
| `model` | string | Device model (e.g., “iPhone”). |
| `os` | string | Device operating system (e.g., “iOS”). |
| `osv` | string | Device operating system version (e.g., “3.1.2”). |
| `hwv` | string | Hardware version of the device (e.g., “5S” for iPhone 5S). |
| `h` | integer | Physical height of the screen in pixels. |
| `w` | integer | Physical width of the screen in pixels. |
| `ppi` | integer | Screen size as pixels per linear inch. |
| `pxratio` | float | The ratio of physical pixels to device-independent pixels (DIPS). |
| `js` | integer | Support for JavaScript, where 0 = no, 1 = yes. |
| `geofetch` | integer | Indicates if the geolocation API will be available to JavaScript code running in the banner, where 0 = no, 1 = yes. |
| `flashver` | string | Version of Flash supported by the browser. |
| `language` | string | Browser language using ISO-639-1-alpha-2. Only one of `language` or `langb` should be present. |
| `langb` | string | Browser language using IETF BCP 47. Only one of `language` or `langb` should be present. |
| `carrier` | string | Carrier or ISP (e.g., “VERIZON”) using exchange curated string names which should be published to bidders *a priori*. |
| `mccmnc` | string | Mobile carrier as the concatenated MCC-MNC code (e.g., “310-005” identifies Verizon Wireless CDMA in the USA). Refer to https://en.wikipedia.org/wiki/Mobile_country_code for further examples. Note that the dash between the MCC and MNC parts is required to remove parsing ambiguity. The MCC-MNC values represent the SIM installed on the device and do not change when a device is roaming. Roaming may be inferred by a combination of the MCC-MNC, geo, IP and other data signals. |
| `connectiontype` | integer | Network connection type. Refer to [List: Connection Types](https://github.com/InteractiveAdvertisingBureau/AdCOM/blob/master/AdCOM%20v1.0%20FINAL.md#list--connection-types-) in AdCOM 1.0. |
| `ifa` | string | ID sanctioned for advertiser use in the clear (i.e., not hashed)<br>Unless prior arrangements have been made between the buyer and the seller directly, the value in this field is expected to be an ID derived from a call to an advertising API provided by the device’s Operating System. |
| `didsha1` | string; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `didmd5` | string; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `dpidsha1` | string; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `dpidmd5` | string; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `macsha1` | string; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `macmd5` | string; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `ext` | object | Placeholder for exchange-specific extensions to OpenRTB. |





# 3.2.20 User

### 3.2.20 - Object: User <a name="objectuser"></a>

This object contains information known or derived about the human user of the device (i.e., the audience for advertising). The user `id` is an exchange artifact and may be subject to rotation or other privacy policies. However, when present, this user ID should be stable long enough to serve reasonably as the basis for frequency capping and retargeting.



| Attribute | Type | Description |
| --- | --- | --- |
| `id` | string | Exchange-specific ID for the user.<br>Unless prior arrangements have been made between the buyer and the seller directly, the value in this field is expected to be the exchange’s user ID from its cookie. |
| `buyeruid` | string | Buyer-specific ID for the user as mapped by the exchange for the buyer.<br>Unless prior arrangements have been made between the buyer and the seller directly, the value in this field is expected to be derived from an ID sync. (see [Appendix: Cookie Based ID Syncing)](#appendixc) |
| `yob` | integer; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `gender` | string; DEPRECATED | Deprecated as of OpenRTB 2.6. |
| `keywords` | string | Comma separated list of keywords, interests, or intent. Only one of `keywords` or `kwarray` may be present. |
| `kwarray` | string array | Array of keywords about the user. Only one of `keywords` or `kwarray` may be present. |
| `customdata` | string | Optional feature to pass bidder data that was set in the exchange’s cookie. The string must be in base85 cookie safe characters and be in any format. Proper JSON encoding must be used to include “escaped” quotation marks. |
| `geo` | object | Location of the user’s home base defined by a `Geo` object (Section 3.2.19). This is not necessarily their current location. |
| `data` | object array | Additional user data. Each `Data` object (Section 3.2.21) represents a different data source. |
| `consent` | string | When GDPR regulations are in effect this attribute contains the Transparency and Consent Framework’s [Consent String](https://github.com/InteractiveAdvertisingBureau/GDPR-Transparency-and-Consent-Framework/blob/master/TCFv2/IAB%20Tech%20Lab%20-%20Consent%20string%20and%20vendor%20list%20formats%20v2.md) data structure. |
| `eids` | object array | Details for support of a standard protocol for multiple third party identity providers (Section 3.2.27). |
| `ext` | object | Placeholder for exchange-specific extensions to OpenRTB. |





# 3.2.27 EID

### 3.2.27 - Object: EID <a name="objecteid"></a>

Extended identifiers support in the OpenRTB specification allows buyers to use audience data in real-time bidding. This object can contain one or more UIDs from a single source or a technology provider. The exchange should ensure that business agreements allow for the sending of this data. See [Section 7.12 of Implementation Guidance](implementation.md#idmm) for additional notes regarding the use of these fields.


| Attribute | Type | Description |
| --- | --- | --- |
| `inserter` | string | The canonical domain name of the entity (publisher, publisher monetization company, SSP, Exchange, Header Wrapper, etc.) that caused the ID array element to be added. This may be the operational domain of the system, if that is different from the parent corporate domain, to facilitate WHOIS and reverse IP lookups to establish clear ownership of the delegate system.<br>This should be the same value as used to identify sellers in an ads.txt file if one exists.<br>For ad tech intermediaries, this would be the domain as used in ads.txt. For publishers, this would match the domain in the `site` or `app` object. |
| `source` | string | Canonical domain of the ID. |
| `matcher` | string | Technology providing the match method as defined in `mm`.<br>In some cases, this may be the same value as inserter.<br>When blank, it is assumed that the `matcher` is equal to the `source`<br>May be omitted when mm=0, 1, or 2. |
| `mm` | int | Match method used by the `matcher`. Refer to [List: ID Match Methods](https://github.com/InteractiveAdvertisingBureau/AdCOM/blob/main/AdCOM%20v1.0%20FINAL.md#list-id-match-methods-) in AdCOM 1.0 |
| `uids` | object array | Array of extended ID `UID` objects from the given source. Refer to the `Extended Identifier UIDs` object (Section 3.2.28) |
| `ext` | object | Placeholder for exchange-specific extensions to OpenRTB. |





# 3.2.28 UID

### 3.2.28 - Object: UID <a name="objectuid"></a>

This object contains a single user identifier provided as part of extended identifiers. The exchange should ensure that business agreements allow for the sending of this data.


| Attribute | Type | Description |
| --- | --- | --- |
| `id` | string | The identifier for the user. |
| `atype` | integer | Type of user agent the ID is from. It is highly recommended to set this, as many DSPs separate app-native IDs from browser-based IDs and require a type value for ID resolution. Refer to [List: Agent Types](https://github.com/InteractiveAdvertisingBureau/AdCOM/blob/master/AdCOM%20v1.0%20FINAL.md#list_agenttypes) in AdCOM 1.0 |
| `ext` | object | Placeholder for vendor specific extensions to this object. |






# Appendix C privacy

Other Considerations and Best Practices
As user IDs can be considered personal data under some privacy regulations, implementers are advised to consult with their counsel and apply appropriate measures for compliance. As examples, however, the following practices are considered customary:
Inclusion of query string parameters for GDPR, US Privacy String, GPP, etc. per the relevant Tech Lab specifications
Based on information like GDPR consent string, a party might gate whether or not they fire a given sync pixel on whether they believe the consent string indicates the appropriate consent for the party
Based on information like a GDPR consent string, a party might elect to treat the event as a no-op — for example, if their sync pixel is fired, the user is in Europe, and consent information is not provided, the party might elect to simply immediately return 204 No Content and take no actions, since user consent is not known

There are several best practices that implementers can follow to ensure the match rate and coverage between parties is maximized:
Cookies have a limited lifespan typically, so it is customary to limit match table retention to some period of time like 14 to 60 days. Parties are suggested to arrange their sync behavior to ensure that the match for a given user is refreshed (if they are still observed active) before expiring out of the match table.
There are frequently a long list of parties necessary to sync. For example, an exchange, for each user, needs to trigger syncs with each and every DSP they work with. Thus, it’s suggested to take all available opportunities to deploy sync pixels, such as when serving ads, when serving tracking tags, etc.
It's also helpful if both parties deploy sync pixels when possible, as this increases the number of opportunities to perform sync for a given user.
Sync pixels fire in the user’s browser, and thus sync activity creates overhead when web pages load. To avoid blocking page loads, parties are advised to load sync pixels in a non-blocking manner, such as in a hidden IFRAME. Additionally, parties might wish to limit the number of sync partners deployed in a given instance to a modest number.
For example, a reasonable strategy would be to sync up to 5 partners on each occasion, and record that this has occurred and when. Then, on the next occasion, the next 5 partners can be synced, and so on. Once all partners have been rotated through and syncs established for a given user, it’s not necessary to fire 