# ADR 0027: Usar Vitest para Testing del Frontend

## Estado

Aceptado

## Contexto

El frontend desarrollado con React + Vite necesita un framework de testing para:
- Tests unitarios de hooks y contextos
- Tests de componentes con React Testing Library
- Tests de integración
- Cobertura de código

Las opciones principales son:
1. **Jest** - El estándar histórico en testing de JavaScript/React
2. **Vitest** - Framework moderno diseñado para Vite
3. **Testing Library solo** - Solo utilidades de testing sin runner

## Decisión

Usamos **Vitest** como framework de testing para el frontend.

### Configuración adoptada:
- `vitest` con `jsdom` como environment
- `@testing-library/react` para testing de componentes
- `@testing-library/jest-dom` para matchers adicionales
- `@vitest/coverage-v8` para cobertura de código
- Tests co-locados junto al código fuente (`*.test.tsx`)

## Justificación

### Integración nativa con Vite
- Comparte la misma configuración de Vite (aliases, plugins)
- No requiere configuración de transformación separada
- Hot Module Replacement en modo watch

### Rendimiento superior
- Ejecución en paralelo por defecto
- Re-ejecución inteligente solo de tests afectados
- Significativamente más rápido que Jest en proyectos Vite

### API compatible con Jest
- Misma sintaxis (`describe`, `it`, `expect`, `vi.mock`)
- Migración trivial desde Jest si fuera necesario
- Documentación y ejemplos abundantes

### Experiencia de desarrollo
- UI interactiva con `vitest --ui`
- Integración nativa con VS Code
- Mejor soporte para ESM y TypeScript

## Alternativas consideradas

### Jest
- **Pros**: Madurez, ecosistema amplio, documentación extensa
- **Contras**: Requiere configuración adicional para Vite, transformadores separados, más lento

### Testing Library solo
- **Pros**: Mínima dependencia
- **Contras**: No es un test runner, necesita combinarse con otro framework

## Consecuencias

### Positivas
- Configuración mínima gracias a la integración con Vite
- Tests más rápidos mejoran el ciclo de desarrollo
- Mismo toolchain que el build de producción

### Negativas
- Ecosistema más pequeño que Jest (aunque creciendo rápidamente)
- Algunos plugins de Jest no tienen equivalente directo

## Referencias

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Vite + Vitest Guide](https://vitest.dev/guide/#configuring-vitest)
