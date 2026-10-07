"""
NITI Aayog Aspirational District flag — DLMAI Layer 1 (Pillar 6).

The list below is the REAL, COMPLETE list of all 112 Aspirational
Districts, fetched directly from NITI Aayog's own published PDF
(niti.gov.in/sites/default/files/2023-07/List-of-112-Aspirational-
Districts%20(1).pdf) -- not a mock or a sample. This is one of the
cleanest sources in the whole project for a structural reason worth
calling out explicitly: because the source list is EXHAUSTIVE (it's the
complete national list, not a partial extract from one state or one
search), a district's absence from it is an unambiguous, confirmed
ZERO -- not an "unknown, not yet collected" the way Jan Aushadhi's or
MCA21's partial pulls are. No covered-vs-uncovered tracking is needed
here at all.

PMJAY/Ayushman Bharat scheme-penetration data, the OTHER half of Pillar 6
in the original framework, is deliberately NOT included here. Confirmed,
not assumed: the live public dashboard (dashboard.pmjay.gov.in) returns a
robots-disallowed response to automated fetches, and the only bulk,
structured PMJAY dataset found on data.gov.in is State/UT-level, not
district-level. That's a genuine, confirmed dead end for a free,
automatable district-level pull right now -- not a gap to quietly route
around by faking district-level numbers from a state-level figure. Pillar
6 in this build is the NITI Aayog flag alone; PMJAY remains a manual-
collection candidate for a future pass, not a fabricated indicator.

VINTAGE NOTE: districts in this list are named after the 2023 edition --
e.g. "Y.S.R. Kadapa" matches this sample's "YSR Kadapa" via the
crosswalk's normalize() function, which strips punctuation precisely so
this kind of formatting difference (periods, spacing) doesn't cause a
false non-match.
"""

ASPIRATIONAL_DISTRICTS = [
    ("Andhra Pradesh", "Alluri Sitharamaraju"), ("Andhra Pradesh", "Parvathipuram Manyam"),
    ("Andhra Pradesh", "Y.S.R. Kadapa"), ("Arunachal Pradesh", "Namsai"),
    ("Assam", "Baksa"), ("Assam", "Barpeta"), ("Assam", "Darrang"), ("Assam", "Dhubri"),
    ("Assam", "Goalpara"), ("Assam", "Hailakandi"), ("Assam", "Udalguri"),
    ("Bihar", "Araria"), ("Bihar", "Aurangabad"), ("Bihar", "Banka"), ("Bihar", "Begusarai"),
    ("Bihar", "Gaya"), ("Bihar", "Jamui"), ("Bihar", "Katihar"), ("Bihar", "Khagaria"),
    ("Bihar", "Muzaffarpur"), ("Bihar", "Nawada"), ("Bihar", "Purnea"), ("Bihar", "Sheikhpura"),
    ("Bihar", "Sitamarhi"),
    ("Chhattisgarh", "Bastar"), ("Chhattisgarh", "Bijapur"), ("Chhattisgarh", "Dantewada"),
    ("Chhattisgarh", "Kanker"), ("Chhattisgarh", "Kondagaon"), ("Chhattisgarh", "Korba"),
    ("Chhattisgarh", "Mahasamund"), ("Chhattisgarh", "Narayanpur"), ("Chhattisgarh", "Rajnandgaon"),
    ("Chhattisgarh", "Sukma"),
    ("Gujarat", "Dahod"), ("Gujarat", "Narmada"),
    ("Haryana", "Mewat"), ("Himachal Pradesh", "Chamba"),
    ("Jammu & Kashmir", "Baramula"), ("Jammu & Kashmir", "Kupwara"),
    ("Jharkhand", "Bokaro"), ("Jharkhand", "Chatra"), ("Jharkhand", "Dumka"),
    ("Jharkhand", "Garhwa"), ("Jharkhand", "Giridih"), ("Jharkhand", "Godda"),
    ("Jharkhand", "Gumla"), ("Jharkhand", "Hazaribag"), ("Jharkhand", "Khunti"),
    ("Jharkhand", "Latehar"), ("Jharkhand", "Lohardaga"), ("Jharkhand", "Pakur"),
    ("Jharkhand", "Palamu"), ("Jharkhand", "Pashchimi Singhbhum"), ("Jharkhand", "Purbi Singhbhum"),
    ("Jharkhand", "Ramgarh"), ("Jharkhand", "Ranchi"), ("Jharkhand", "Sahibganj"),
    ("Jharkhand", "Simdega"),
    ("Karnataka", "Raichur"), ("Karnataka", "Yadgir"),
    ("Kerala", "Wayanad"),
    ("Madhya Pradesh", "Barwani"), ("Madhya Pradesh", "Chhatarpur"), ("Madhya Pradesh", "Damoh"),
    ("Madhya Pradesh", "Guna"), ("Madhya Pradesh", "Khandwa"), ("Madhya Pradesh", "Rajgarh"),
    ("Madhya Pradesh", "Singrauli"), ("Madhya Pradesh", "Vidisha"),
    ("Maharashtra", "Gadchiroli"), ("Maharashtra", "Nandurbar"), ("Maharashtra", "Osmanabad"),
    ("Maharashtra", "Washim"),
    ("Manipur", "Chandel"), ("Meghalaya", "Ribhoi"), ("Mizoram", "Mamit"), ("Nagaland", "Kiphire"),
    ("Odisha", "Balangir"), ("Odisha", "Dhenkanal"), ("Odisha", "Gajapati"), ("Odisha", "Kalahandi"),
    ("Odisha", "Kandhamal"), ("Odisha", "Koraput"), ("Odisha", "Malkangiri"),
    ("Odisha", "Nabarangapur"), ("Odisha", "Nuapada"), ("Odisha", "Rayagada"),
    ("Punjab", "Ferozepur"), ("Punjab", "Moga"),
    ("Rajasthan", "Baran"), ("Rajasthan", "Dholpur"), ("Rajasthan", "Jaisalmer"),
    ("Rajasthan", "Karauli"), ("Rajasthan", "Sirohi"),
    ("Sikkim", "Soreng"),
    ("Tamil Nadu", "Ramanathapuram"), ("Tamil Nadu", "Virudhunagar"),
    ("Telangana", "Asifabad"), ("Telangana", "Bhadradri-Kothagudem"), ("Telangana", "Bhupalpally"),
    ("Tripura", "Dhalai"),
    ("Uttar Pradesh", "Bahraich"), ("Uttar Pradesh", "Balrampur"), ("Uttar Pradesh", "Chandauli"),
    ("Uttar Pradesh", "Chitrakoot"), ("Uttar Pradesh", "Fatehpur"), ("Uttar Pradesh", "Shravasti"),
    ("Uttar Pradesh", "Siddharthnagar"), ("Uttar Pradesh", "Sonbhadra"),
    ("Uttarakhand", "Haridwar"), ("Uttarakhand", "Udham Singh Nagar"),
]
assert len(ASPIRATIONAL_DISTRICTS) == 112, f"expected 112 districts, got {len(ASPIRATIONAL_DISTRICTS)}"


def flag_aspirational_districts(crosswalk) -> dict:
    """
    Returns {lgd_code: 1} for every district in the crosswalk's master that
    matches an entry in the real Aspirational Districts list. Districts
    NOT returned here should be set to 0 by the caller -- their absence is
    a confirmed zero (this source is exhaustive), not a missing value.
    """
    flagged = {}
    for state, district in ASPIRATIONAL_DISTRICTS:
        result = crosswalk.resolve(district, state_hint=state)
        if result.lgd_code:
            flagged[result.lgd_code] = 1
    return flagged
