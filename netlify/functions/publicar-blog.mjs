// Publica os artigos agendados do blog.
// Toda segunda-feira às 12:00 UTC (9h em Brasília), dispara um novo deploy no Netlify.
// O build roda _blog/build_blog.py, que só coloca no ar os artigos com data igual ou anterior a hoje.
// A URL do build hook fica na variável de ambiente BLOG_BUILD_HOOK (Netlify > Project configuration > Environment variables).
export default async () => {
  const hook = process.env.BLOG_BUILD_HOOK;
  if (!hook) {
    console.log("BLOG_BUILD_HOOK não configurado.");
    return new Response("sem hook", { status: 500 });
  }
  const r = await fetch(hook, { method: "POST" });
  console.log("Build do blog disparado:", r.status);
  return new Response("ok");
};

export const config = { schedule: "0 12 * * 1" };
