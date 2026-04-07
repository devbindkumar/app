import { Copy, Check } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../components/ui/dialog";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../../components/ui/tabs";
import { Badge } from "../../components/ui/badge";

/**
 * Macros Reference Dialog Component
 */
export function MacrosDialog({ open, onOpenChange, macros }) {
  const [copiedMacro, setCopiedMacro] = useState(null);

  const copyMacro = async (macro) => {
    try {
      await navigator.clipboard.writeText(macro);
      setCopiedMacro(macro);
      toast.success(`Copied ${macro}`);
      setTimeout(() => setCopiedMacro(null), 2000);
    } catch {
      toast.error("Failed to copy");
    }
  };

  if (!macros) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            OpenRTB Macros Reference
            <Badge className="bg-[#3B82F6]/10 text-[#3B82F6]">
              {macros.total_macros} macros
            </Badge>
          </DialogTitle>
        </DialogHeader>
        
        <div className="flex-1 overflow-auto">
          <Tabs defaultValue={macros.categories?.[0]?.name || "auction"} className="w-full">
            <TabsList className="w-full flex-wrap h-auto gap-1 mb-4 bg-slate-100 p-1">
              {macros.categories?.map((category) => (
                <TabsTrigger 
                  key={category.name} 
                  value={category.name}
                  className="text-xs px-3 py-1.5 data-[state=active]:bg-white"
                >
                  {category.name}
                  <Badge className="ml-1.5 bg-slate-200 text-slate-600 text-[10px] px-1.5">
                    {category.macros.length}
                  </Badge>
                </TabsTrigger>
              ))}
            </TabsList>
            
            {macros.categories?.map((category) => (
              <TabsContent key={category.name} value={category.name} className="mt-0">
                <div className="p-2">
                  <div className="grid grid-cols-1 gap-1">
                    {category.macros.map((m) => (
                      <div 
                        key={m.macro}
                        onClick={() => copyMacro(m.macro)}
                        className="flex items-center justify-between p-2 hover:bg-slate-50 rounded cursor-pointer group transition-colors"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <code className="text-xs font-mono text-[#3B82F6] bg-[#3B82F6]/10 px-2 py-0.5 rounded">
                              {m.macro}
                            </code>
                            {copiedMacro === m.macro ? (
                              <Check className="w-3.5 h-3.5 text-[#10B981]" />
                            ) : (
                              <Copy className="w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            )}
                          </div>
                          <p className="text-xs text-slate-500 mt-1 truncate">
                            {m.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </div>
        
        <div className="mt-4 pt-4 border-t border-slate-200">
          <p className="text-xs text-slate-500 text-center">
            Click any macro to copy it to clipboard. Paste it into your pixel URL.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default MacrosDialog;
