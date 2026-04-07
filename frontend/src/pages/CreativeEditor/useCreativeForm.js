import { useState, useCallback } from "react";
import { toast } from "sonner";
import { 
  getCreative, 
  getCreativeMacros, 
  uploadImage, 
  uploadVideo, 
  uploadAudio 
} from "../../lib/api";
import { BANNER_SIZES, INITIAL_FORM_STATE } from "./constants";

/**
 * Custom hook for managing Creative Editor form state and handlers
 */
export function useCreativeForm(id) {
  const isEdit = !!id;
  
  // Form state
  const [form, setForm] = useState({
    ...INITIAL_FORM_STATE,
    name: "",
    status: "active",
    imageUrl: "",
    backgroundColor: "#ffffff",
    clickUrl: "",
    vastUrl: "",
    vastVersion: "4.0",
    videoDuration: "30",
    videoWidth: "1920",
    videoHeight: "1080",
    videoUrl: "",
    audioUrl: "",
    audioVastUrl: "",
    audioVastXml: "",
    audioDuration: "30",
    audioMimes: "audio/mpeg,audio/mp3,audio/ogg",
    companionBannerUrl: "",
    companionWidth: "300",
    companionHeight: "250",
    nativeTitle: "",
    nativeDescription: "",
    nativeIconUrl: "",
    nativeImageUrl: "",
    nativeCtaText: "Learn More",
    nativeCtaColor: "#3B82F6",
    nativeClickUrl: "",
    jsTagContent: "",
    jsTagUrl: "",
    jsTagWidth: "300",
    jsTagHeight: "250",
    jsTagVendor: "",
    jsTagType: "script",
    jsTagIsSecure: true,
    cat: "",
    adomain: "",
  });
  
  // UI state
  const [creativeType, setCreativeType] = useState("banner");
  const [selectedSize, setSelectedSize] = useState(BANNER_SIZES[0]);
  const [useCustomSize, setUseCustomSize] = useState(false);
  const [customWidth, setCustomWidth] = useState(300);
  const [customHeight, setCustomHeight] = useState(250);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [uploadedVideo, setUploadedVideo] = useState(null);
  const [uploadedAudio, setUploadedAudio] = useState(null);
  const [videoSourceType, setVideoSourceType] = useState("vast");
  const [audioSourceType, setAudioSourceType] = useState("vast");
  const [impressionPixels, setImpressionPixels] = useState([]);
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  // Macros
  const [macros, setMacros] = useState(null);
  const [macrosLoading, setMacrosLoading] = useState(false);
  const [showMacrosDialog, setShowMacrosDialog] = useState(false);
  
  const updateField = useCallback((field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
  }, []);

  const loadCreative = useCallback(async () => {
    if (!id) return;
    
    setLoading(true);
    try {
      const response = await getCreative(id);
      const creative = response.data;
      
      if (creative) {
        setCreativeType(creative.type || "banner");
        
        // Set form fields based on creative type
        const newForm = { ...form };
        newForm.name = creative.name || "";
        newForm.status = creative.status || "active";
        newForm.cat = (creative.cat || []).join(", ");
        newForm.adomain = (creative.adomain || []).join(", ");
        newForm.clickUrl = creative.click_url || "";
        
        if (creative.type === "banner" && creative.banner_data) {
          const hrefMatch = creative.banner_data.ad_markup?.match(/href="([^"]+)"/);
          if (hrefMatch) {
            newForm.clickUrl = hrefMatch[1];
          }
          const imgMatch = creative.banner_data.ad_markup?.match(/src="([^"]+)"/);
          if (imgMatch) {
            newForm.imageUrl = imgMatch[1];
          }
          
          // Set banner size
          if (creative.banner_data?.width && creative.banner_data?.height) {
            const w = creative.banner_data.width;
            const h = creative.banner_data.height;
            const standardSize = BANNER_SIZES.find(s => s.w === w && s.h === h);
            if (standardSize) {
              setSelectedSize(standardSize);
            } else {
              setUseCustomSize(true);
              setCustomWidth(w);
              setCustomHeight(h);
            }
          }
        }
        
        if (creative.type === "video" && creative.video_data) {
          newForm.vastUrl = creative.video_data.vast_url || "";
          newForm.vastVersion = creative.video_data.vast_version || "4.0";
          newForm.videoDuration = String(creative.video_data.duration || 30);
          newForm.videoWidth = String(creative.video_data.width || 1920);
          newForm.videoHeight = String(creative.video_data.height || 1080);
          newForm.videoUrl = creative.video_data.video_url || "";
          setVideoSourceType(creative.video_data.source_type || "vast");
        }
        
        if (creative.type === "native" && creative.native_data) {
          newForm.nativeTitle = creative.native_data.title || "";
          newForm.nativeDescription = creative.native_data.description || creative.native_data.desc || "";
          newForm.nativeIconUrl = creative.native_data.icon_url || "";
          newForm.nativeImageUrl = creative.native_data.main_image_url || creative.native_data.image_url || "";
          newForm.nativeCtaText = creative.native_data.cta_text || "Learn More";
          newForm.nativeClickUrl = creative.native_data.click_url || "";
        }
        
        if (creative.type === "audio" && creative.audio_data) {
          newForm.audioUrl = creative.audio_data.audio_url || "";
          newForm.audioVastUrl = creative.audio_data.vast_url || "";
          newForm.audioDuration = String(creative.audio_data.duration || 30);
          newForm.companionBannerUrl = creative.audio_data.companion_banner_url || "";
          newForm.companionWidth = String(creative.audio_data.companion_width || 300);
          newForm.companionHeight = String(creative.audio_data.companion_height || 250);
          setAudioSourceType(creative.audio_data.audio_url ? "upload" : "vast");
        }
        
        if (creative.type === "js_tag" && creative.js_tag_data) {
          newForm.jsTagContent = creative.js_tag_data.tag_content || "";
          newForm.jsTagUrl = creative.js_tag_data.tag_url || "";
          newForm.jsTagWidth = String(creative.js_tag_data.width || 300);
          newForm.jsTagHeight = String(creative.js_tag_data.height || 250);
          newForm.jsTagVendor = creative.js_tag_data.vendor || "";
          newForm.jsTagType = creative.js_tag_data.tag_type || "script";
          newForm.jsTagIsSecure = creative.js_tag_data.is_secure !== false;
        }
        
        // Load impression pixels
        if (creative.impression_pixels && Array.isArray(creative.impression_pixels)) {
          setImpressionPixels(creative.impression_pixels);
        }
        
        setForm(newForm);
      }
    } catch {
      toast.error("Failed to load creative");
    } finally {
      setLoading(false);
    }
  }, [id]);

  const loadMacros = useCallback(async () => {
    if (macros) {
      setShowMacrosDialog(true);
      return;
    }
    
    setMacrosLoading(true);
    try {
      const response = await getCreativeMacros();
      setMacros(response.data);
      setShowMacrosDialog(true);
    } catch {
      toast.error("Failed to load macros");
    } finally {
      setMacrosLoading(false);
    }
  }, [macros]);

  const handleImageUpload = useCallback(async (file) => {
    if (!file) return;
    
    setUploading(true);
    try {
      const res = await uploadImage(file);
      const imageData = res.data;
      
      if (creativeType === "banner") {
        updateField("imageUrl", imageData.url);
        setUploadedImages(prev => [...prev, imageData]);
      } else if (creativeType === "native") {
        updateField("nativeImageUrl", imageData.url);
      }
      
      toast.success("Image uploaded successfully");
    } catch {
      toast.error("Failed to upload image");
    } finally {
      setUploading(false);
    }
  }, [creativeType, updateField]);

  const handleVideoUpload = useCallback(async (file) => {
    if (!file) return;
    
    const allowedTypes = ["video/mp4", "video/webm", "video/ogg"];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Invalid video format. Allowed: MP4, WebM, OGG");
      return;
    }
    
    setUploading(true);
    try {
      const tempBlobUrl = URL.createObjectURL(file);
      
      const video = document.createElement('video');
      video.src = tempBlobUrl;
      video.onloadedmetadata = () => {
        const duration = Math.round(video.duration);
        updateField("videoDuration", String(duration));
        updateField("videoWidth", String(video.videoWidth));
        updateField("videoHeight", String(video.videoHeight));
      };
      
      const response = await uploadVideo(file);
      const serverUrl = response.data.url;
      
      setUploadedVideo(serverUrl);
      updateField("videoUrl", serverUrl);
      
      URL.revokeObjectURL(tempBlobUrl);
      toast.success("Video uploaded successfully");
    } catch {
      toast.error("Failed to upload video");
    } finally {
      setUploading(false);
    }
  }, [updateField]);

  const handleAudioUpload = useCallback(async (file) => {
    if (!file) return;
    
    const allowedTypes = ["audio/mpeg", "audio/mp3", "audio/ogg", "audio/wav", "audio/aac"];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Invalid audio format. Allowed: MP3, OGG, WAV, AAC");
      return;
    }
    
    setUploading(true);
    try {
      const tempBlobUrl = URL.createObjectURL(file);
      
      const audio = document.createElement('audio');
      audio.src = tempBlobUrl;
      audio.onloadedmetadata = () => {
        const duration = Math.round(audio.duration);
        updateField("audioDuration", String(duration));
      };
      
      const response = await uploadAudio(file);
      const serverUrl = response.data.url;
      
      setUploadedAudio(serverUrl);
      updateField("audioUrl", serverUrl);
      
      URL.revokeObjectURL(tempBlobUrl);
      toast.success("Audio uploaded successfully");
    } catch {
      toast.error("Failed to upload audio");
    } finally {
      setUploading(false);
    }
  }, [updateField]);

  const handleCompanionUpload = useCallback(async (file) => {
    if (!file) return;
    
    setUploading(true);
    try {
      const res = await uploadImage(file);
      updateField("companionBannerUrl", res.data.url);
      toast.success("Companion banner uploaded");
    } catch {
      toast.error("Failed to upload companion banner");
    } finally {
      setUploading(false);
    }
  }, [updateField]);

  // Impression Pixel handlers
  const addImpressionPixel = useCallback(() => {
    setImpressionPixels(prev => [...prev, {
      id: `pixel-${Date.now()}`,
      name: "",
      url: "",
      event: "impression",
      enabled: true
    }]);
  }, []);

  const updateImpressionPixel = useCallback((index, field, value) => {
    setImpressionPixels(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  }, []);

  const removeImpressionPixel = useCallback((index) => {
    setImpressionPixels(prev => prev.filter((_, i) => i !== index));
  }, []);

  const toggleImpressionPixel = useCallback((index) => {
    setImpressionPixels(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], enabled: !updated[index].enabled };
      return updated;
    });
  }, []);

  return {
    // Form state
    form,
    setForm,
    updateField,
    
    // Creative type
    creativeType,
    setCreativeType,
    
    // Size state
    selectedSize,
    setSelectedSize,
    useCustomSize,
    setUseCustomSize,
    customWidth,
    setCustomWidth,
    customHeight,
    setCustomHeight,
    
    // Upload state
    uploadedImages,
    uploadedVideo,
    uploadedAudio,
    uploading,
    
    // Source types
    videoSourceType,
    setVideoSourceType,
    audioSourceType,
    setAudioSourceType,
    
    // Impression pixels
    impressionPixels,
    addImpressionPixel,
    updateImpressionPixel,
    removeImpressionPixel,
    toggleImpressionPixel,
    
    // Loading states
    loading,
    saving,
    setSaving,
    
    // Macros
    macros,
    macrosLoading,
    showMacrosDialog,
    setShowMacrosDialog,
    loadMacros,
    
    // Actions
    loadCreative,
    handleImageUpload,
    handleVideoUpload,
    handleAudioUpload,
    handleCompanionUpload,
    
    // Meta
    isEdit,
  };
}
