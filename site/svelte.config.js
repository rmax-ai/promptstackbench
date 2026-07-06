import adapter from "@sveltejs/adapter-static";

const isDev = process.argv.includes("dev");

const config = {
  kit: {
    adapter: adapter({ pages: "../docs", assets: "../docs", fallback: undefined }),
    paths: {
      base: isDev ? "" : "/promptstackbench",
    },
  },
};

export default config;
