---
date: 2025-10-24
categories:
  - Programming
---

# The State of Javascript Linting (and Formatting)

Summary:
- ESLint is really slow
- Biome is faster, but doesn't fully support all ESLint plugins like `eslint-plugin-react-hooks`. Also, the VSCode extension doesn't work to fix import sorting, import sorting clashes with VSCode, and Prettier plugins like `prettier-plugin-tailwindcss` don't work.

<!-- more -->

Oxlint is promising, but the formatter isn't ready yet (and it can't sort imports via a VSCode action yet either).

The best combination of tools now would probably be Oxlint for linting, and Prettier for formatting (with `prettier-plugin-tailwindcss` for Tailwind CSS class sorting).
