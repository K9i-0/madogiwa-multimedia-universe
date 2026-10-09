// Only the server theme loader is replaced; the real clip pages are rendered.
export const Route = { useLoaderData: () => ({ clipTheme: 'sakaba' as const }) };
