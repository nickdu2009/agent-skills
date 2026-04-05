from phase_contract.schema import REQUIRED_LANE_FIELDS, REQUIRED_WAVE_FIELDS


def validate_phase_execution_schema(plan):
    errors = []

    for index, wave in enumerate(plan.get("waves", []), start=1):
        for field in REQUIRED_WAVE_FIELDS:
            if field not in wave:
                errors.append(f"wave {index}: missing {field}")

        lanes = wave.get("lane", [])
        if not lanes:
            errors.append(f"wave {index}: missing lanes")
            continue

        for lane_index, lane in enumerate(lanes, start=1):
            for field in REQUIRED_LANE_FIELDS:
                if field not in lane:
                    errors.append(f"wave {index} lane {lane_index}: missing {field}")

    return errors
