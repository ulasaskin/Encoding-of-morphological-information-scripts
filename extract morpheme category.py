#THIS SCRIPT TAKES THE LABELLED MORPHOLOGICAL TIER AND COPIES IT. THEN FOR EACH MORPHEME CATEGORY IT
#CHANGES ITS LABEL ACCORDING TO THE category_map DICTIONARY.

!pip install tgt
import tgt

def add_category_tier(input_file, output_file, morph_tier_name, control_tier_name = "control"):
    try:
        tg = tgt.io.read_textgrid(input_file, encoding='utf-16')
    except:
        tg = tgt.io.read_textgrid(input_file, encoding='utf-8')

    if not tg.has_tier(morph_tier_name):
        print(f"Error: Tier '{morph_tier_name}' not found!")
        return

    source_tier = tg.get_tier_by_name(morph_tier_name)
    has_control = tg.has_tier(control_tier_name)
    control_tier = tg.get_tier_by_name(control_tier_name) if has_control else None

    #my category = number mapping where i numbered each functional category as a number
    category_map = {
        "R": "1",# Root
        #VERBAL INFLECTION
        #VOICE
        "PASS": "2",# Passive
        "CAUS": "3",# Causative
        "REFL": "4",# Reflexive
        "RECP": "5",# Recipient
        #MODALITY (modals and nominals)
        "ABIL": "6",# Abilitative
        "INF": "7", # Infinitive
        "NEG": "8", # Negation
        "NMLZ": "9", # Nominalizer
        "IMP": "28", # Imperative
        #TAM 1 (tense, aspect and mood)
        "PST": "10", # Past
        "EV": "11", # Evidential
        "COND": "12", # Conditional
        "AOR": "13", # Aorist
        "FUT": "14", # Future
        "PROG": "15", # Progressive
        "OBL": "16", # Obligative
        "OPT": "17", # Optative
        "PTCP": "18", # Participle
        "CVB": "19", # Converb
        #AGREEMENT (S-V)
        "A1SG": "20",
        "A2SG": "20",
        "A3SG": "20",
        "A1PL": "20",
        "A2PL": "20",
        "A3PL": "20",
        #NOMINAL INFLECTION
        "COP": "21", # Copula
        "ADJZ": "22", # Adjectivizer
        "VBLZ": "23", # Verbalizer
        "PL": "24", # Plural
        "REL": "25", # Relativizer
        "ADD": "26", # Additive -ki
        #NOMINAL AGREEMENT (possessives)
        "P1SG": "27",
        "P2SG": "27",
        "P3SG": "27",
        "P1PL": "27",
        "P2PL": "27",
        "P3PL": "27",
        #CASE
        "ACC": "29", # Accusative
        "DAT": "30", # Dative
        "GEN": "31", # Genitive
        "LOC": "32", # Locative
        "ABL": "33", # Ablative
        "INSTR": "34", # Instrumental
        "AG": "35", # Agentive
        #QUESTION PARTICLE
        "Q": "36", # Question {-mI}
    }

    #make a category tier
    category_tier = tgt.IntervalTier(start_time=tg.start_time,
                                     end_time=tg.end_time,
                                     name="category")

    print(f"\n--- Processing: {input_file} ---")
    mismatch_count = 0

    for interval in source_tier:
        raw_label = interval.text.strip().upper()

        is_overlapping = False
        if has_control:
            for ctrl_int in control_tier:
                if (interval.start_time < ctrl_int.end_time) and (interval.end_time > ctrl_int.start_time):
                    if "<OVR>" in ctrl_int.text.upper():
                        is_overlapping = True
                        break

        
        if is_overlapping or not raw_label:
            new_label = ""
        elif raw_label.startswith(("#", "[", "(", "<")):
            new_label = raw_label
        elif raw_label in category_map:
            new_label = category_map[raw_label]
        else:
            mismatch_count += 1
            new_label = "0" 


        category_tier.add_interval(tgt.Interval(interval.start_time, interval.end_time, new_label))

    tg.add_tier(category_tier)
    tgt.io.write_to_file(tg, output_file, format='long')
    print(f"Success! Category tier generated with {mismatch_count} mismatches.")



#run by changing the input file name, output file name and/or the tier names based on your input file
add_category_tier("tripod_TR_ex-01_complexity.TextGrid", "tripod_TR_ex-01_complexity_category.TextGrid", "morphology", "control")
