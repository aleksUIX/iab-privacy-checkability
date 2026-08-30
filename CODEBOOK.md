# Syntax / meaning codebook

Unit of analysis: a normative statement in an IAB privacy spec, or a privacy-relevant field row in OpenRTB 2.6.

This codebook is **not** paper 2's A/B/C/D. Those classes answer "can a machine decide conformance to the spec." This axis answers "does deciding conformance decide anything about the person."

A statement gets one syntax class and one meaning class. Paper 2 class is recorded as a third, inherited label so the two papers stay comparable.

## Syntax (can a receiver reject the bytes)

**S0** Not a wire artifact. Implementation-guide prose about org process, contracts, or UI.

**S1** Shape. Alphabet, version bits, length floor, enum, 0/1, presence of a paired field (`gpp` with `gpp_sid`). rtblint/pixellint already do this.

**S2** Internal consistency of the artifact. GPP header section count vs payloads after `~`; TCF version bits vs declared TCF; `ifa_type` vs `device.make` (paper 4 dismissed this as jointly sender-controlled; still S2).

**S3** Cross-artifact syntax. String in the bid vs string in the VAST macro vs string on the SSAI beacon. Checkable if you have both hops. Paper 2 class C.

## Meaning (does a pass imply the legal or user fact)

**M0** No person-fact. Pure transport ("carry the string if present").

**M1** Meaning is delegated to a named source of truth that is not in the message. A CMP wrote the TC string; the OS set LAT; a store age-rating marked the app. The bid cannot confirm that source. Pass/fail on S does not transfer.

**M2** Meaning is the sender's word. `regs.coppa=1` means the sender asserts COPPA. No public registry rejects a lie. Same structure as paper 4 class C (self-declared).

**M3** Meaning is outside this contract. ACR fingerprints, HbbTV pixels, vendor CAPI on a different pipe. An IAB-valid bid is silent.

## Inherited paper-2 class

A / B / C / D as in *How Machine-Checkable Is OpenRTB?*, applied only to the privacy subset. Expected pattern: lots of A/B on S1, lots of D or C on M1/M2.

## Coding rules

1. Code the spec's own claim, not the press-release claim. GPP "streamlines transmission of privacy signals" is S1+M1, not "GDPR compliance."
2. Deprecated artifacts stay in the corpus (US Privacy; `regs.ext.gdpr`). Deprecation is a finding.
3. `regs.coppa` is S1 + M2. Do not upgrade it to M1 by imagining a kids-app registry unless the spec names one.
4. `device.ifa` presence is S1. Limit-ad-tracking and reset cadence are M1 (OS) or M2 (SSAI-supplied IFA). Paper 4: SSAI can originate the identifier.
5. VAST `[GDPRCONSENT]` is S3 relative to the bid's `user.consent`. A tag with an unexpanded macro is trafficking, already handled in pixellint; a fired tag with a different string than the bid is the interesting S3 case. Do not invent a rate without a paired corpus.
6. Surface 2 (ACR) statements are not extracted from IAB specs. They are a boundary row: M3, syntax n/a.
7. Vendor hash contracts (Meta `em` is SHA-256, IP is not) are S1 + M0 for the hash, M1 for "user consented to this event." One table, not a second dataset.

## Reliability

Author first pass. Delayed recode of 40 of 221 statements (seed 20260822). Report kappa, or report disagreement concentrated on M1 vs M2, X vs conformance, and TCF bit-field enums.

## What a "green" GPP check means in the paper

It means S1/S2 passed. The abstract must not say it means consent.
