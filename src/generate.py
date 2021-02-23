# VS Code color scheme generator

from pathlib import Path
import os
import json


# build all theme definitions in `themes` into a VS code extension in `build`.
def main():
    Path('build/themes').mkdir(parents=True, exist_ok=True)

    themes = []
    for filename in os.listdir('themes'):
        path = f'themes/{filename}'
        label, kind, theme = build_theme(path)

        print(label)

        with open(f'build/{path}', 'w') as file:
            json.dump(theme, file, indent=4)

        themes.append({
            'label': label,
            'uiTheme': 'vs' if kind == 'light' else 'vs-dark',
            'path': path,
        })

    package = {
        'name': 'colorful',
        'displayName': 'Colorful',
        'description': 'Dark and light colorful theme.',
        'version': '0.0.1',
        'engines': { 'vscode': '^1.35.0' },
        'categories': ['Themes'],
        'contributes': {
            'themes': themes
        }
    }

    with open('build/package.json', 'w') as file:
        json.dump(package, file, indent=4)


# compile a single theme from a specification at a path
def build_theme(path):
    with open(path) as file:
        spec = json.load(file)

    label = spec.pop('theme')
    kind = spec.pop('kind')
    base = spec.pop('base')

    with open(f'base/{base}.json') as file:
        theme = json.load(file)

    with open('src/scopes.json') as file:
        scopes = json.load(file)

    theme['type'] = kind
    theme['colors']['editor.foreground'] = spec.pop('foreground')
    theme['colors']['editor.background'] = spec.pop('background')

    colors = theme['tokenColors']
    new_colors = []

    for name, value in spec.items():
        selected = scopes.get(name, name)
        settings = {}

        if value.startswith('#'):
            settings['foreground'] = value[:7]

        styles = [s for s in ('italic', 'bold', 'underline') if s in value]
        if styles:
            settings['fontStyle'] = ' '.join(styles)

        entry = {
            'scope': selected,
            'settings': settings,
        }

        # Remove the newly defined scopes from all base definitions.
        if type(selected) == str:
            defined = [selected]
        else:
            defined = selected

        i = 0
        while i < len(colors):
            s = colors[i]['scope']

            if type(s) == str and any(s.startswith(d) for d in defined):
                del colors[i]
                continue

            if type(s) == list:
                for d in defined:
                    colors[i]['scope'] = [v for v in s
                        if not any(v.startswith(d) for d in defined)]

                if not s:
                    del colors[i]
                    continue

            i += 1

        new_colors.append(entry)

    for entry in new_colors:
        colors.append(entry)

    return label, kind, theme


if __name__ == '__main__':
    main()
