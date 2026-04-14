import { Image, Video, Film, Music, Code, Play } from "lucide-react";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";

/**
 * Creative Preview Component - Renders preview based on creative type
 */
export function CreativePreview({ 
  creativeType, 
  form, 
  selectedSize, 
  useCustomSize, 
  customWidth, 
  customHeight,
  videoSourceType,
  audioSourceType 
}) {
  if (creativeType === "banner") {
    return (
      <BannerPreview 
        form={form} 
        selectedSize={selectedSize}
        useCustomSize={useCustomSize}
        customWidth={customWidth}
        customHeight={customHeight}
      />
    );
  }
  
  if (creativeType === "native") {
    return <NativePreview form={form} />;
  }
  
  if (creativeType === "video") {
    return <VideoPreview form={form} videoSourceType={videoSourceType} />;
  }
  
  if (creativeType === "audio") {
    return <AudioPreview form={form} audioSourceType={audioSourceType} />;
  }
  
  if (creativeType === "js_tag") {
    return <JsTagPreview form={form} />;
  }
  
  return null;
}

function BannerPreview({ form, selectedSize, useCustomSize, customWidth, customHeight }) {
  const previewWidth = useCustomSize ? customWidth : selectedSize.w;
  const previewHeight = useCustomSize ? customHeight : selectedSize.h;
  
  return (
    <div 
      style={{ 
        width: previewWidth, 
        height: previewHeight,
        background: form.backgroundColor,
        overflow: "hidden"
      }}
      className="border border-slate-200 rounded"
    >
      {form.imageUrl ? (
        <img 
          src={form.imageUrl} 
          alt="Preview" 
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : (
        <div className="flex items-center justify-center h-full text-slate-500">
          <Image className="w-8 h-8" />
        </div>
      )}
    </div>
  );
}

function NativePreview({ form }) {
  return (
    <div className="w-[320px] p-4 bg-white rounded border border-slate-200">
      <div className="flex items-start gap-3">
        {form.nativeIconUrl && (
          <img src={form.nativeIconUrl} alt="Icon" className="w-12 h-12 rounded" />
        )}
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-900">{form.nativeTitle || "Ad Title"}</p>
          <p className="text-xs text-gray-500">Sponsored</p>
        </div>
      </div>
      {form.nativeImageUrl && (
        <img src={form.nativeImageUrl} alt="Main" className="w-full h-40 object-cover mt-3 rounded" />
      )}
      <p className="text-sm text-gray-700 mt-2">{form.nativeDescription || "Ad description..."}</p>
      <a 
        href={form.nativeClickUrl || "#"}
        target="_blank"
        rel="noopener noreferrer"
        className="block mt-3 w-full py-2 rounded text-white text-sm text-center cursor-pointer hover:opacity-90 transition-opacity"
        style={{ background: form.nativeCtaColor }}
        onClick={(e) => !form.nativeClickUrl && e.preventDefault()}
      >
        {form.nativeCtaText || "Learn More"}
      </a>
    </div>
  );
}

function VideoPreview({ form, videoSourceType }) {
  return (
    <div className="w-full max-w-[480px] aspect-video bg-[#000] rounded border border-slate-200 overflow-hidden">
      {videoSourceType === "upload" && form.videoUrl ? (
        <video 
          src={form.videoUrl} 
          controls 
          className="w-full h-full object-contain"
        >
          Your browser does not support the video tag.
        </video>
      ) : videoSourceType === "vast" && form.vastUrl ? (
        <div className="w-full h-full flex flex-col items-center justify-center text-center p-4">
          <Film className="w-16 h-16 text-[#3B82F6] mb-4" />
          <p className="text-slate-900 font-medium">VAST Tag Preview</p>
          <Badge className="mt-2 bg-[#3B82F6]/20 text-[#3B82F6]">
            VAST {form.vastVersion}
          </Badge>
          <p className="text-xs text-slate-500 mt-3 break-all max-w-full">
            {form.vastUrl.length > 60 ? form.vastUrl.substring(0, 60) + "..." : form.vastUrl}
          </p>
          <p className="text-xs text-slate-600 mt-2">Duration: {form.videoDuration}s</p>
          <Button
            size="sm"
            className="mt-4 bg-[#10B981] hover:bg-[#10B981]/90"
            onClick={() => window.open(form.vastUrl, '_blank')}
          >
            <Play className="w-3 h-3 mr-1" />
            Test VAST Tag
          </Button>
        </div>
      ) : (
        <div className="w-full h-full flex items-center justify-center text-slate-500">
          <Video className="w-12 h-12" />
        </div>
      )}
    </div>
  );
}

function AudioPreview({ form, audioSourceType }) {
  const previewWidth = parseInt(form.companionWidth) || 300;
  const previewHeight = parseInt(form.companionHeight) || 250;
  
  return (
    <div className="w-full max-w-[400px] space-y-4">
      {/* Companion Banner Preview */}
      {form.companionBannerUrl && (
        <div 
          className="rounded-lg border border-slate-200 overflow-hidden bg-slate-100"
          style={{ 
            width: Math.min(previewWidth, 380), 
            height: Math.min(previewHeight, 300),
            margin: '0 auto'
          }}
        >
          <img 
            src={form.companionBannerUrl} 
            alt="Companion Banner" 
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        </div>
      )}
      
      {/* Audio Player Section */}
      <div className="p-4 bg-gradient-to-br from-[#EC4899]/10 to-[#8B5CF6]/10 rounded-lg border border-slate-200">
        {audioSourceType === "upload" && form.audioUrl ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-[#EC4899]/20 flex items-center justify-center shrink-0">
                <Music className="w-6 h-6 text-[#EC4899]" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-slate-900 font-medium">Audio Preview</p>
                <p className="text-xs text-slate-600">Duration: {form.audioDuration}s</p>
              </div>
            </div>
            <audio src={form.audioUrl} controls className="w-full" />
          </div>
        ) : audioSourceType === "vast" && (form.audioVastUrl || form.audioVastXml) ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-[#EC4899]/20 flex items-center justify-center shrink-0">
                <Music className="w-6 h-6 text-[#EC4899]" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-slate-900 font-medium">Audio VAST Tag</p>
                <Badge className="mt-1 bg-[#EC4899]/20 text-[#EC4899]">
                  {form.audioDuration}s Audio
                </Badge>
              </div>
            </div>
            {form.audioVastUrl && (
              <>
                <p className="text-xs text-slate-500 break-all">
                  {form.audioVastUrl.length > 50 ? form.audioVastUrl.substring(0, 50) + "..." : form.audioVastUrl}
                </p>
                <Button
                  size="sm"
                  className="w-full bg-[#EC4899] hover:bg-[#EC4899]/90"
                  onClick={() => window.open(form.audioVastUrl, '_blank')}
                >
                  Test VAST Tag
                </Button>
              </>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-slate-500">
            <Music className="w-10 h-10 mb-2" />
            <p className="text-sm">Configure audio settings</p>
          </div>
        )}
      </div>
      
      {/* Size info display */}
      {form.companionBannerUrl && (
        <p className="text-xs text-center text-slate-500">
          Banner: {previewWidth}x{previewHeight}px
        </p>
      )}
    </div>
  );
}

function JsTagPreview({ form }) {
  const livePreviewHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { 
          width: 100%; 
          height: 100%; 
          display: flex; 
          align-items: center; 
          justify-content: center;
          background: #f5f5f5;
          overflow: hidden;
        }
        .ad-container {
          width: ${form.jsTagWidth || 300}px;
          height: ${form.jsTagHeight || 250}px;
          position: relative;
          background: #fff;
          border: 1px solid #ddd;
          overflow: hidden;
        }
      </style>
    </head>
    <body>
      <div class="ad-container">
        ${form.jsTagContent || ''}
      </div>
    </body>
    </html>
  `;
  
  return (
    <div className="w-full max-w-[450px] space-y-4">
      {/* Header Info */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#F59E0B]/20 flex items-center justify-center shrink-0">
            <Code className="w-5 h-5 text-[#F59E0B]" />
          </div>
          <div>
            <p className="text-sm text-slate-900 font-medium">Third Party JS Tag</p>
            <div className="flex items-center gap-2 mt-1">
              {form.jsTagVendor && (
                <Badge className="bg-[#F59E0B]/20 text-[#F59E0B] text-xs">
                  {form.jsTagVendor}
                </Badge>
              )}
              <Badge className="bg-[#64748B]/20 text-slate-600 text-xs">
                {form.jsTagType}
              </Badge>
              {form.jsTagIsSecure && (
                <Badge className="bg-[#10B981]/20 text-[#10B981] text-xs">
                  HTTPS
                </Badge>
              )}
            </div>
          </div>
        </div>
        <Badge className="bg-[#3B82F6]/20 text-[#3B82F6]">
          {form.jsTagWidth || 300}x{form.jsTagHeight || 250}
        </Badge>
      </div>

      {/* Live Preview Area */}
      {form.jsTagContent ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500">Live Ad Preview</p>
            <Badge className="bg-[#10B981]/20 text-[#10B981] text-xs animate-pulse">LIVE</Badge>
          </div>
          <div 
            className="rounded-lg border-2 border-dashed border-[#3B82F6]/30 bg-slate-50 p-4 flex items-center justify-center"
            style={{ minHeight: Math.min((parseInt(form.jsTagHeight) || 250) + 40, 350) }}
          >
            <iframe
              srcDoc={livePreviewHtml}
              title="Ad Preview"
              width={Math.min((parseInt(form.jsTagWidth) || 300) + 20, 420)}
              height={Math.min((parseInt(form.jsTagHeight) || 250) + 20, 320)}
              className="border-0"
              sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
            />
          </div>
          <p className="text-xs text-slate-400 text-center">
            Note: Some third-party tags may not render in preview due to security restrictions
          </p>
        </div>
      ) : form.jsTagUrl ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-500">External Tag URL</p>
            <Badge className="bg-[#3B82F6]/20 text-[#3B82F6] text-xs">URL</Badge>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <code className="text-xs text-slate-600 break-all">{form.jsTagUrl}</code>
          </div>
          <p className="text-xs text-slate-400 text-center">
            External JS tags load at runtime and cannot be previewed here
          </p>
        </div>
      ) : (
        <div className="rounded-lg border-2 border-dashed border-slate-200 p-8 flex flex-col items-center justify-center text-slate-500">
          <Code className="w-10 h-10 mb-3" />
          <p className="text-sm">Paste JS tag content or enter URL to preview</p>
        </div>
      )}
    </div>
  );
}

export default CreativePreview;
