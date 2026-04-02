import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, CheckCircle2, Download, Loader2, Mail, FileSpreadsheet, Settings } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { batchPredictUpload } from '@/lib/api';
import { toast } from 'sonner';

export default function BatchUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);

  const [dryRun, setDryRun] = useState(false);
  const [sendEmails, setSendEmails] = useState(true);
  const [includeCsv, setIncludeCsv] = useState(true);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1
  });

  const handleProcess = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(10);
    setResult(null);

    const progInt = setInterval(() => {
      setProgress(p => Math.min(p + Math.random() * 20, 90));
    }, 500);

    try {
      const res = await batchPredictUpload(file, sendEmails, dryRun, includeCsv);
      clearInterval(progInt);
      setProgress(100);
      setResult(res);
      toast.success("Batch completed successfully");
      if (res.email_mode === "stub" && res.send_emails && !res.dry_run) {
        toast.warning("SMTP not configured; set Gmail credentials in backend/.env.");
      }
    } catch (err) {
      console.error(err);
      clearInterval(progInt);
      toast.error("Batch processing failed");
    } finally {
      setTimeout(() => {
         setUploading(false);
         setProgress(0);
      }, 500);
    }
  };

  const handleDownload = () => {
    if (!result?.enriched_csv_base64) return;
    const decoded = atob(result.enriched_csv_base64);
    const blob = new Blob([decoded], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'batch_enriched.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col space-y-8 w-full max-w-[1200px] mx-auto pb-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Batch Campaign Manager</h1>
        <p className="text-muted-foreground mt-1">Upload CSV cohorts to bulk analyze churn risk.</p>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="rounded-2xl border-border/50 shadow-sm overflow-hidden bg-card">
          <CardContent className="p-0">
            <div 
              {...getRootProps()} 
              className={`p-10 border-2 border-dashed mx-6 mt-6 rounded-2xl flex flex-col items-center justify-center text-center cursor-pointer transition-all ${isDragActive ? 'border-primary bg-primary/5' : 'border-border/60 hover:bg-secondary/40'} ${file ? 'bg-secondary/10 border-primary/20' : ''}`}
            >
              <input {...getInputProps()} />
              
              {!file ? (
                <>
                  <div className="h-16 w-16 mb-4 rounded-full bg-secondary flex items-center justify-center">
                    <UploadCloud className="h-8 w-8 text-primary/80" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Drop your CSV file here</h3>
                  <p className="text-muted-foreground max-w-sm">Drag and drop, or click to browse. Ensure headers match the customer profile schema.</p>
                </>
              ) : (
                <>
                  <div className="h-16 w-16 mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                    <File className="h-8 w-8 text-primary tracking-tight font-bold" />
                  </div>
                  <h3 className="text-xl font-semibold mb-1 text-primary">{file.name}</h3>
                  <p className="text-muted-foreground text-sm">{(file.size / 1024).toFixed(2)} KB • Ready to process</p>
                </>
              )}
            </div>

            {/* Required columns hint */}
            {!file && (
               <div className="mt-4 px-8 pb-6 text-sm text-muted-foreground">
                 <p className="font-semibold text-foreground mb-2 whitespace-nowrap">Required columns include:</p>
                 <ul className="list-disc pl-5 space-y-1">
                    <li><strong className="text-foreground">user_id</strong> (or customer_id) and <strong className="text-foreground">email</strong></li>
                    <li>All model fields: gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService, MultipleLines, InternetService, OnlineSecurity, etc.</li>
                    <li>Optional: days_since_last_login, avg_logins_per_week, avg_session_duration_minutes, feature_usage_score, etc.</li>
                    <li><em>Churn column is ignored if present.</em></li>
                 </ul>
               </div>
            )}
          </CardContent>
          
          <AnimatePresence>
             {file && !result && (
               <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="px-6 py-6 border-t border-border/50 flex flex-col gap-6">
                 
                 <div className="bg-secondary/20 p-4 rounded-xl border border-border/50 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <label className="flex flex-row items-center justify-between rounded-lg border p-3 cursor-pointer hover:bg-secondary/30 transition-colors">
                       <div className="space-y-0.5">
                         <div className="text-sm font-medium flex items-center gap-2"><Settings className="w-4 h-4"/> Dry run</div>
                         <div className="text-xs text-muted-foreground">(no emails sent)</div>
                       </div>
                       <input type="checkbox" checked={dryRun} onChange={e => setDryRun(e.target.checked)} className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary" />
                    </label>
                    <label className="flex flex-row items-center justify-between rounded-lg border p-3 cursor-pointer hover:bg-secondary/30 transition-colors">
                       <div className="space-y-0.5">
                         <div className="text-sm font-medium flex items-center gap-2"><Mail className="w-4 h-4"/> Send real emails</div>
                       </div>
                       <input type="checkbox" checked={sendEmails} onChange={e => setSendEmails(e.target.checked)} className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary" />
                    </label>
                    <label className="flex flex-row items-center justify-between rounded-lg border p-3 cursor-pointer hover:bg-secondary/30 transition-colors">
                       <div className="space-y-0.5">
                         <div className="text-sm font-medium flex items-center gap-2"><FileSpreadsheet className="w-4 h-4"/> Include CSV</div>
                         <div className="text-xs text-muted-foreground">Return enriched CSV</div>
                       </div>
                       <input type="checkbox" checked={includeCsv} onChange={e => setIncludeCsv(e.target.checked)} className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary" />
                    </label>
                 </div>

                 <div className="flex items-center justify-end">
                    <Button onClick={handleProcess} disabled={uploading} className="rounded-xl px-8 h-10 w-full sm:w-auto">
                       {uploading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                       {uploading ? 'Processing Batch...' : 'Run Batch Job'}
                    </Button>
                 </div>
                 {uploading && (
                   <div className="space-y-2 mb-2">
                     <div className="flex justify-between text-xs font-semibold text-muted-foreground">
                        <span>Uploading & scoring...</span>
                        <span>{Math.round(progress)}%</span>
                     </div>
                     <Progress value={progress} className="h-2" />
                   </div>
                 )}
               </motion.div>
             )}
          </AnimatePresence>
        </Card>
      </motion.div>

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 gap-6">
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <Card className="rounded-2xl shadow-sm border-border/50 bg-card">
                 <CardContent className="p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-1 uppercase tracking-wider">Total users</p>
                    <p className="text-2xl font-bold">{result.total_users}</p>
                 </CardContent>
              </Card>
              <Card className="rounded-2xl shadow-sm border-border/50 bg-card">
                 <CardContent className="p-4">
                    <p className="text-xs font-medium text-red-500 mb-1 uppercase tracking-wider">High risk (≥70%)</p>
                    <p className="text-2xl font-bold">{result.high_risk_users}</p>
                 </CardContent>
              </Card>
              <Card className="rounded-2xl shadow-sm border-border/50 bg-card">
                 <CardContent className="p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-1 uppercase tracking-wider">Emails sent</p>
                    <p className="text-2xl font-bold">{result.emails_sent}</p>
                 </CardContent>
              </Card>
              <Card className="rounded-2xl shadow-sm border-border/50 bg-card">
                 <CardContent className="p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-1 uppercase tracking-wider">Failed/Blocked</p>
                    <p className="text-2xl font-bold">{result.failed}</p>
                 </CardContent>
              </Card>
              <Card className="rounded-2xl shadow-sm border-border/50 bg-card">
                 <CardContent className="p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-1 uppercase tracking-wider">Eligible</p>
                    <p className="text-2xl font-bold">{result.would_send}</p>
                 </CardContent>
              </Card>
            </div>

            <Card className="rounded-2xl shadow-sm border-border/50 bg-card flex flex-col items-center justify-center py-10 text-center">
              <CheckCircle2 className="h-16 w-16 text-green-500 mb-4" />
              <h3 className="text-2xl font-bold mb-6">Batch Executed</h3>
              {result.email_mode === "stub" && result.send_emails && !result.dry_run && (
                <div className="bg-yellow-500/10 text-yellow-500 text-sm font-medium py-2 px-4 rounded-lg mb-6 border border-yellow-500/20 max-w-md">
                   SMTP not configured; set Gmail credentials in backend/.env.
                </div>
              )}
              {result.enriched_csv_base64 && (
                <Button onClick={handleDownload} className="rounded-xl" variant="outline">
                   <Download className="mr-2 h-4 w-4" /> Download Enriched CSV
                </Button>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
