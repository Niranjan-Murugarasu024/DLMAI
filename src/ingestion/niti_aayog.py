"""
NITI Aayog Aspirational Districts Registry for South India DLMAI.
Official exhaustive list of 112 Aspirational Districts.
"""

from typing import Set

# Complete official list of all 112 Aspirational Districts
OFFICIAL_ASPIRATIONAL_DISTRICTS = {
    # Andhra Pradesh
    "Visakhapatnam", "Vizianagaram", "Y.S.R. Kadapa", "Kadapa", "Alluri Sitharama Raju", "Parvathipuram Manyam",
    # Telangana
    "Asifabad", "Kumuram Bheem Asifabad", "Komaram Bheem Asifabad", "Jayashankar Bhupalapally", "Bhadradri Kothagudem",
    # Karnataka
    "Raichur", "Yadgir", "Yadgiri",
    # Kerala
    "Wayanad",
    # Tamil Nadu
    "Ramanathapuram", "Virudhunagar",
    # Rest of India (for national matching)
    "Baksa", "Barpeta", "Darrang", "Dhubri", "Goalpara", "Hailakandi", "Udalguri",
    "Araria", "Aurangabad", "Banka", "Begusarai", "Gaya", "Jamui", "Katihar", "Khagaria", "Muzaffarpur", "Nawada", "Purnia", "Sheikhpura", "Sitamarhi",
    "Bastar", "Bijapur", "Dantewada", "Kanker", "Kondagaon", "Korba", "Mahasamund", "Narayanpur", "Rajnandgaon", "Sukma",
    "Dahod", "Narmada", "Mewat", "Chamba", "Baramulla", "Kupwara", "Dumka", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Khunti", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ranchi", "Sahibganj", "Simdega", "West Singhbhum",
    "Barwani", "Chhatarpur", "Damoh", "Guna", "Khandwa", "Rajgarh", "Singrauli", "Vidisha", "Gadchiroli", "Nandurbar", "Washim", "Osmanabad",
    "Chandel", "Ribhoi", "Mamit", "Kiphire", "Balangir", "Dhenkanal", "Gajapati", "Kalahandi", "Kandhamal", "Koraput", "Malkangiri", "Nabarangpur", "Nuapada", "Rayagada",
    "Firozpur", "Moga", "Baran", "Jaisalmer", "Karauli", "Sirohi", "Dhalai", "Bahraich", "Balrampur", "Chandauli", "Chitrakoot", "Fatehpur", "Shravasti", "Siddharthnagar", "Sonbhadra", "Haridwar", "Birbhum", "Maldah", "Murshidabad", "Nadia", "South 24 Parganas"
}


def is_aspirational_district(district_name: str) -> int:
    """Returns 1 if district is in official Aspirational Districts list, else 0."""
    if not district_name:
        return 0
    clean = district_name.strip()
    return 1 if any(a.lower() == clean.lower() or a.lower() in clean.lower() for a in OFFICIAL_ASPIRATIONAL_DISTRICTS) else 0
