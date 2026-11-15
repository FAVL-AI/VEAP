const core = process.env.VEAP_CORE_ORIGIN || "http://127.0.0.1:8000";
const studio = process.env.VEAP_STUDIO_ORIGIN || "http://127.0.0.1:8010";
export default {
  async rewrites() {
    return [
      {
        source: "/api/studio/:path*",
        destination: studio + "/api/studio/:path*",
      },
      { source: "/api/:path*", destination: core + "/api/:path*" },
    ];
  },
};
