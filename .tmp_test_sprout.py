import sys
sys.path[:0] = [
    "/Volumes/ExternalDocs/Documents/openscad_boardgame_toolkit/.venv/lib/python3.14/site-packages",
    "/Volumes/ExternalDocs/Documents/openscad_boardgame_toolkit/examples",
    "/Volumes/ExternalDocs/Documents/openscad_boardgame_toolkit"
]
try:
    import compartments
    compartments._realise = lambda groups, plan, height: []
    
    from compartments import Compartment, Group, Shape, Removal, PackingBin, layout_compartments
    from collections import namedtuple
    import random
    
    box_width = 288
    box_length = 158
    default_wall_thickness = 2.0
    animal_token_thickness = 8.0
    
    ANIMAL_PIECES = [
        ("elephant", 43.5, 54.0, 1),
        ("polar_bear", 36.5, 53.0, 1),
        ("cow", 36.5, 47.5, 1),
        ("pig", 24.5, 35.0, 1),
        ("gazelle", 41.0, 35.0, 1),
        ("turkey", 24.0, 125.0, 1),
        ("fly", 11.0, 11.0, 1),
        ("capybara", 16.5, 64.0, 1),
        ("capybara_2", 16.5, 96.0, 1),
        ("monkey", 29.0, 24.0, 1),
        ("pangolin", 16.0, 105.0, 1),
        ("deer", 47.0, 25.5, 1),
        ("goanna", 25.0, 30.0, 1),
        ("fox", 16.0, 35.0, 1),
        ("snake", 14.0, 41.5, 1),
        ("rabbit", 18.5, 21.0, 1),
        ("termite", 12.0, 60.0, 1),
        ("ornyx", 39.0, 40.0, 1),
        ("platypus", 14.5, 25.0, 1),
        ("lemur", 22.0, 30.0, 1),
        ("peacock", 30.0, 27.0, 1),
        ("gopher", 17.5, 85.0, 1),
        ("crocodile", 16.0, 85.0, 1),
        ("goat", 37.0, 36.0, 1),
        ("jaguar", 20.0, 49.0, 1),
        ("rhino", 36.0, 64.0, 1),
        ("goose", 25.0, 21.0, 1),
        ("eagle", 31.0, 43.0, 1),
        ("spider_monkey", 26.5, 25.0, 1),
        ("hoopoe", 17.0, 16.0, 1),
        ("kangaroo", 37.0, 39.0, 1),
        ("loon", 26.5, 13.0, 1),
        ("tarsier", 29.0, 12.5, 1),
        ("jay", 12.5, 12.0, 1),
        ("chipmunk", 15.0, 14.0, 1),
        ("quokka", 24.0, 15.0, 1),
        ("beaver", 15.5, 35.0, 1),
    ]
    
    inner_w = box_width - (default_wall_thickness * 2 + 72) - 38.0 - 2 * 1.5
    inner_l = box_length - 2 * 1.5
    InnerSize = namedtuple("InnerSize", ["width", "length", "height"])
    inner = InnerSize(width=inner_w, length=inner_l, height=12.5)
    
    def get_length_needed(box_items):
        comps = [Compartment(w=w, l=l, depth=animal_token_thickness, label=name, rotate=True) for name, w, l, num in box_items]
        low = 50.0
        high = 500.0
        for _ in range(10):
            mid = (low + high) / 2.0
            test_inner = InnerSize(width=inner_w, length=mid, height=12.5)
            try:
                layout_compartments([Group(comps, packing=PackingBin.BBF)], min_gap=1.5)(test_inner)
                high = mid
            except Exception:
                low = mid
        return high

    # Run multiple times with different random initial splits
    for attempt in range(10):
        random.shuffle(ANIMAL_PIECES)
        split = len(ANIMAL_PIECES) // 2
        box1 = ANIMAL_PIECES[:split]
        box2 = ANIMAL_PIECES[split:]
        
        best_score = max(get_length_needed(box1), get_length_needed(box2))
        print(f"Attempt {attempt} Initial Max Length: {best_score:.1f}")
        
        improved = True
        steps = 0
        while improved and steps < 1000:
            improved = False
            steps += 1
            
            for i in range(len(box1)):
                for j in range(len(box2)):
                    b1 = list(box1)
                    b2 = list(box2)
                    b1[i], b2[j] = b2[j], b1[i]
                    
                    l1 = get_length_needed(b1)
                    l2 = get_length_needed(b2)
                    score = max(l1, l2)
                    
                    if score < best_score:
                        box1 = b1
                        box2 = b2
                        best_score = score
                        improved = True
                        print(f"Step {steps}: Improved Max Length to {best_score:.1f} (Box1: {l1:.1f}, Box2: {l2:.1f})")
                        if best_score <= 155.0:
                            break
                if best_score <= 155.0:
                    break
                    
            if best_score <= 155.0:
                print("SUCCESS! Found valid partition!")
                print("Box 1 pieces:")
                for item in sorted(box1):
                    print(f"        {item!r},")
                print("Box 2 pieces:")
                for item in sorted(box2):
                    print(f"        {item!r},")
                sys.exit(0)
            
    print("Failed to find valid partition.")
    sys.exit(1)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
