import Redis from "ioredis";

let redis = new Redis(process.env.REDIS_URL);

export default async function handler(req, res) {
  if (req.method === "GET") {
    await get(req, res);
  }
}

async function get(req, res) {
  let hits = parseInt((await redis.get("hits")) || "1");
  res.status(200).json({ hits: hits });
  redis.set("hits", hits + 1);
}
