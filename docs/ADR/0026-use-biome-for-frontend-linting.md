# ADR-0026: Usar Biome para linting y formateo del frontend

## Estado
Aceptada

## Contexto
El proyecto backend utiliza pre-commit hooks con ruff, black, isort y mypy para garantizar calidad de código Python. Para mantener consistencia, necesitamos herramientas equivalentes para el frontend TypeScript/React.

Las opciones evaluadas fueron:
1. **ESLint + Prettier**: Stack tradicional, configuración compleja, múltiples dependencias
2. **Biome**: Herramienta moderna todo-en-uno (linting + formatting), escrita en Rust, muy rápida

## Decisión
Usaremos **Biome** como linter y formateador para el frontend por las siguientes razones:

1. **Todo-en-uno**: Combina linting (como ESLint) y formateo (como Prettier) en una sola herramienta
2. **Rendimiento**: Escrito en Rust, es 10-100x más rápido que ESLint/Prettier
3. **Configuración simple**: Un solo archivo `biome.json` en lugar de múltiples configs
4. **Filosofía similar a ruff**: Biome es para JavaScript/TypeScript lo que ruff es para Python
5. **Organización de imports**: Incluye ordenamiento automático de imports (reemplaza isort)

## Configuración
```json
{
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "linter": {
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedVariables": "warn",
        "noUnusedImports": "warn"
      }
    }
  },
  "assist": {
    "actions": {
      "source": {
        "organizeImports": "on"
      }
    }
  }
}
```

## Scripts de npm
```json
{
  "lint": "biome check src/",
  "lint:fix": "biome check --write src/",
  "format": "biome format --write src/",
  "check": "biome check --write --unsafe src/"
}
```

## Pre-commit hooks
Se añaden hooks locales para ejecutar Biome y TypeScript check en archivos del frontend:
```yaml
- repo: local
  hooks:
    - id: biome-check
      name: biome check
      entry: bash -c 'cd frontend && npx biome check --write src/'
      language: system
      files: ^frontend/src/.*\.(ts|tsx|js|jsx|json)$

    - id: typescript-check
      name: typescript
      entry: bash -c 'cd frontend && npx tsc --noEmit'
      language: system
      files: ^frontend/src/.*\.(ts|tsx)$
```

## Consecuencias

### Positivas
- Verificación de código consistente entre backend (ruff) y frontend (biome)
- Pre-commit hooks garantizan código limpio antes de cada commit
- Detección temprana de errores de TypeScript
- Formateo automático uniforme

### Negativas
- Algunos warnings de `any` en catch blocks de axios (aceptable como warning)
- Requiere excluir archivos generados (shadcn/ui components, CSS de Tailwind)

## Alternativas descartadas
- **ESLint + Prettier**: Más establecido pero más lento y complejo de configurar
- **Solo TypeScript**: No incluye reglas de estilo ni formateo automático

## Referencias
- [Biome](https://biomejs.dev/)
- [Migración desde ESLint](https://biomejs.dev/guides/migrate-eslint-prettier/)
