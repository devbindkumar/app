// Creative Editor Constants and Configuration

export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Standard banner sizes
export const BANNER_SIZES = [
  { label: "Medium Rectangle", w: 300, h: 250 },
  { label: "Leaderboard", w: 728, h: 90 },
  { label: "Wide Skyscraper", w: 160, h: 600 },
  { label: "Half Page", w: 300, h: 600 },
  { label: "Large Rectangle", w: 336, h: 280 },
  { label: "Billboard", w: 970, h: 250 },
  { label: "Mobile Banner", w: 320, h: 50 },
  { label: "Mobile Large", w: 320, h: 100 },
  { label: "Square", w: 250, h: 250 },
];

// VAST versions
export const VAST_VERSIONS = [
  { value: "2.0", label: "VAST 2.0" },
  { value: "3.0", label: "VAST 3.0" },
  { value: "4.0", label: "VAST 4.0" },
  { value: "4.1", label: "VAST 4.1" },
  { value: "4.2", label: "VAST 4.2 (Latest)" },
];

// Creative templates
export const TEMPLATES = [
  { id: "simple-image", name: "Simple Image Ad", description: "Single image with click-through", type: "banner" },
  { id: "cta-banner", name: "CTA Banner", description: "Image with call-to-action button", type: "banner" },
  { id: "native-article", name: "Native Article", description: "Native ad format for content feeds", type: "native" },
  { id: "video-preroll", name: "Video Pre-Roll", description: "Standard video ad format", type: "video" },
];

// Initial form state
export const INITIAL_FORM_STATE = {
  name: "",
  status: "active",
  type: "banner",
  // Banner
  ad_markup: "",
  click_url: "",
  // Video
  vast_url: "",
  vast_version: "4.0",
  duration: 30,
  skip_offset: 5,
  video_url: "",
  video_bitrate: 2500,
  companion_banners: [],
  // Audio
  audio_url: "",
  audio_vast_url: "",
  audio_vast_version: "4.0",
  audio_duration: 30,
  audio_skip_offset: 5,
  // Native
  native_title: "",
  native_description: "",
  native_cta: "Learn More",
  native_sponsored: "",
  native_image_url: "",
  native_icon_url: "",
  native_rating: "",
  native_price: "",
  native_downloads: "",
  native_likes: "",
  // JS Tag
  js_tag: "",
  js_tag_type: "third_party",
};
