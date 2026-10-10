"""
Lint all the challenge.yml files

```
python3 scripts/lint.py
```
"""

import os
import yaml

def main():
    challenges = []
    for f in os.listdir('high-challenges'):
        if f == 'pages' or f == '.ctf':
            continue
        if os.path.isdir(f'high-challenges/{f}'):
            challenges.append(f'high-challenges/{f}')
    for f in os.listdir('under-challenges'):
        if f == 'pages' or f == '.ctf':
            continue
        if os.path.isdir(f'under-challenges/{f}'):
            challenges.append(f'under-challenges/{f}')
    
    for challenge in challenges:
        try:
            lint(challenge)
        except Exception as e:
            print(f"Error in {challenge}: {e}")
            raise

def lint(challenge):
    # Load the challenge.yml file
    try:
        with open(f"{challenge}/challenge.yml") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f'Error: {challenge}/challenge.yml not found')
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return
    
    # Must have 'flag' section
    if not data.get("flags"):
        raise ValueError("flag section is required")

    if "welcome" in data.get('name'):
        return  

    if data.get('state') != 'hidden':
        print(f'Warning: {challenge}/challenge.yml state is not set to hidden')

    # Ensure it is set to type: dynamic
    if data.get("type") != "dynamic":
        raise ValueError("type must be set to dynamic")

    # Must have 'extra' section
    if not data.get("extra"):
        raise ValueError("extra section is required")
    
    extra = data.get("extra")
    
    if not extra.get('initial') == 500:
        raise ValueError("extra: initial must be set to 500")
    if not extra.get('decay') == 10:
        raise ValueError("extra: decay must be set to 100")
    if not extra.get('minimum') == 50:
        raise ValueError("extra: minimum must be set to 50")

    if data.get('connection_info'):
        print(f'Warning: {challenge}/challenge.yml has connection_info')

    # If the protocol is non-null, must have image set to '.'
    if data.get('protocol') and not data.get('image') == '.':
        raise ValueError("image must be set to '.' if protocol is set")
    if not data.get('protocol') and data.get('image') is not None:
        raise ValueError("protocol must be set if image is set to '.'")

if __name__ == "__main__":
    main()
