#THIS SCRIPT TAKES THE LABELLED MORPHOLOGY TIER AND COPIES IT. TO ANNOTATE MORPHEME DEPTH
#WE UTILIZED A WORD COMPLEXITY METRIC WHERE ROOT IS QUANTIFIED AS 1 AND EACH SUBSEQUENT MORPHEME
#ADDITION INCREASES THIS NUMBER BY +1. THE SCRIPT FUNCTIONS BASED ON THIS SIMPLE LOGIC. IN THE TXTGRIDS,
#EACH ROOT IS LABELLED AS R AND THIS SCRIPT DETERMINES WORD EDGES BASED ON THAT. AFTER EACH R THE
#ADDITION PROCESS RESETS.
!pip install tgt
import tgt

def add_smart_complexity_tier(input_file, output_file, morph_tier_name, control_tier_name="control"):
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

    complexity_tier = tgt.IntervalTier(start_time=tg.start_time,
                                       end_time=tg.end_time,
                                       name="complexity")

    current_count = 0

    for interval in source_tier:
        label = interval.text.strip()

        # --- ROBUST OVR SKIPPING LOGIC ---
        is_overlapping = False
        if has_control:
            # get_annotations_between_endpoints is the standard method for IntervalTiers
            try:
                ovr_check = control_tier.get_annotations_between_endpoints(interval.start_time, interval.end_time)
                if any("<OVR>" in c.text.upper() for c in ovr_check):
                    is_overlapping = True
            except AttributeError:
                # ULTIMATE FALLBACK: Manual overlap check if the library methods fail
                for ctrl_int in control_tier:
                    # Check if intervals overlap: (StartA < EndB) and (EndA > StartB)
                    if (interval.start_time < ctrl_int.end_time) and (interval.end_time > ctrl_int.start_time):
                        if "<OVR>" in ctrl_int.text.upper():
                            is_overlapping = True
                            break

        # LOGIC 1: OVERLAP OR EMPTY (Reset)
        if is_overlapping or not label:
            current_count = 0
            new_label = ""

        # LOGIC 2: COMMENTS (Preserve)
        elif label.startswith(("#", "[", "(", "<")):
            new_label = label

        # LOGIC 3: ROOT (R)
        elif label.upper() == "R":
            current_count = 1
            new_label = str(current_count)

        # LOGIC 4: SUFFIXES
        else:
            if current_count > 0:
                current_count += 1
            else:
                current_count = 1
            new_label = str(current_count)

        new_int = tgt.Interval(interval.start_time, interval.end_time, new_label)
        complexity_tier.add_interval(new_int)

    tg.add_tier(complexity_tier)
    tgt.io.write_to_file(tg, output_file, format='long')
    print(f"Success! Complexity tier created in: {output_file}")

# --- EXECUTION ---
input_filename = "tripod_TR_ex-01-DONE_UA.TextGrid"
output_filename = "tripod_TR_ex-01_complexity.TextGrid"
tier_to_process = "morphology"

add_smart_complexity_tier(input_filename, output_filename, tier_to_process, "control")
