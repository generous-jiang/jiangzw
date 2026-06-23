// Shared icon rasterizer used by both build.js (PPTX) and preview.js (SVG).
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const FA = require("react-icons/fa");

const ICONS = {
  logo: FA.FaRobot,
  w1: FA.FaExchangeAlt, w2: FA.FaTruckLoading, w3: FA.FaWarehouse, w4: FA.FaHandPointer, w5: FA.FaShippingFast,
  cA: FA.FaServer, cB: FA.FaMicrochip, cC: FA.FaUsersCog,
};

async function rasterize(key, hex, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(ICONS[key], { color: "#" + hex, size: String(size) }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return png.toString("base64");
}

module.exports = { ICONS, rasterize };
