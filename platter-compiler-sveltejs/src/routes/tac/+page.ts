// frontend/src/routes/+page.ts
import { base } from '$app/paths';

export async function load() {
  return {
    basePath: base
  };
}
