import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { defaultCustomerPayload, simulateUser } from '@/lib/api';
import { Loader2, ArrowRight, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

export default function Simulation() {
  const [baseUser] = useState(defaultCustomerPayload);
  const [updates, setUpdates] = useState({
    avg_logins_per_week: 4.0,
    days_since_last_login: 8,
    feature_usage_score: 68.0,
    payment_failures_90d: 0,
    Contract: "One year",
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const res = await simulateUser(baseUser, updates);
      setResult(res);
      toast.success("Simulation complete");
    } catch (err) {
      console.error(err);
      toast.error("Failed to run simulation");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    if (risk === 'Low') return 'bg-green-500/10 text-green-500 border-green-500/20';
    if (risk === 'Medium') return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    return 'bg-red-500/10 text-red-500 border-red-500/20';
  };

  return (
    <div className="flex flex-col md:flex-row gap-8 w-full max-w-[1400px] mx-auto pb-10">
      
      <div className="w-full md:w-1/2 lg:w-5/12">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <Card className="rounded-2xl border-border/50 shadow-sm">
            <CardHeader>
              <CardTitle>Engage Simulation</CardTitle>
              <CardDescription>Adjust variables to see how it affects churn probability</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              
              <div className="space-y-4">
                <div className="flex justify-between items-center bg-secondary/20 p-3 rounded-lg border border-border/40">
                  <Label className="text-base text-foreground font-medium">Logins per Week</Label>
                  <span className="font-mono bg-background px-3 py-1 rounded-md text-sm shadow-sm border">{updates.avg_logins_per_week.toFixed(1)}</span>
                </div>
                <Slider
                  defaultValue={[updates.avg_logins_per_week]}
                  max={20}
                  step={0.5}
                  onValueChange={(val) => setUpdates({...updates, avg_logins_per_week: val[0]})}
                  className="py-4 cursor-pointer"
                />
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center bg-secondary/20 p-3 rounded-lg border border-border/40">
                  <Label className="text-base text-foreground font-medium">Days Since Last Login</Label>
                  <span className="font-mono bg-background px-3 py-1 rounded-md text-sm shadow-sm border">{updates.days_since_last_login}</span>
                </div>
                <Slider
                  defaultValue={[updates.days_since_last_login]}
                  max={90}
                  step={1}
                  onValueChange={(val) => setUpdates({...updates, days_since_last_login: val[0]})}
                  className="py-4 cursor-pointer"
                />
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center bg-secondary/20 p-3 rounded-lg border border-border/40">
                  <Label className="text-base text-foreground font-medium">Feature Usage Score</Label>
                  <span className="font-mono bg-background px-3 py-1 rounded-md text-sm shadow-sm border">{updates.feature_usage_score.toFixed(1)}</span>
                </div>
                <Slider
                  defaultValue={[updates.feature_usage_score]}
                  max={100}
                  step={1}
                  onValueChange={(val) => setUpdates({...updates, feature_usage_score: val[0]})}
                  className="py-4 cursor-pointer"
                />
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center bg-secondary/20 p-3 rounded-lg border border-border/40">
                  <Label className="text-base text-foreground font-medium">Payment Failures (90d)</Label>
                  <span className="font-mono bg-background px-3 py-1 rounded-md text-sm shadow-sm border">{updates.payment_failures_90d}</span>
                </div>
                <Slider
                  defaultValue={[updates.payment_failures_90d]}
                  max={5}
                  step={1}
                  onValueChange={(val) => setUpdates({...updates, payment_failures_90d: val[0]})}
                  className="py-4 cursor-pointer"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-base font-medium">Scenario Contract Type</Label>
                <select 
                  className="flex h-10 w-full items-center justify-between rounded-xl border border-input bg-secondary/30 px-3 py-2 text-sm ring-offset-background disabled:opacity-50"
                  value={updates.Contract} 
                  onChange={e => setUpdates({...updates, Contract: e.target.value})}
                >
                  <option value="Month-to-month">Month-to-month</option>
                  <option value="One year">One year</option>
                  <option value="Two year">Two year</option>
                </select>
              </div>

              <Button 
                onClick={handleSimulate} 
                className="w-full rounded-xl h-12 text-md mt-6 shadow-sm shadow-primary/20" 
                disabled={loading}
              >
                {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : null}
                {loading ? 'Running Simulation...' : 'Run Simulation'}
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="w-full md:w-1/2 lg:w-7/12">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="h-full">
           <Card className="rounded-2xl border-border/50 shadow-soft-dark overflow-hidden h-full relative">
             <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/10 pointer-events-none"></div>
             
             <CardContent className="h-full flex flex-col p-10 relative z-10">
               {!result && !loading ? (
                 <div className="flex items-center justify-center h-full text-center opacity-70">
                    <p>Change sliders on the left <br/>and click 'Run Simulation' to see impact.</p>
                 </div>
               ) : loading ? (
                 <div className="flex flex-col items-center justify-center h-full text-center">
                    <Loader2 className="h-10 w-10 text-primary animate-spin" />
                    <p className="mt-4 font-medium animate-pulse">Running What-If Analysis...</p>
                 </div>
               ) : (
                 <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col flex-1">
                    <h3 className="text-xl font-bold mb-4">Intervention Impact</h3>
                    
                    <div className="flex items-center justify-between gap-4 w-full">
                       
                       <div className="flex-1 flex flex-col items-center p-6 bg-secondary/30 rounded-2xl border border-border/50">
                          <p className="text-sm font-medium text-muted-foreground uppercase tracking-widest mb-2">Before</p>
                          <div className="text-4xl font-bold">{(result.original_probability * 100).toFixed(1)}%</div>
                          <p className={`text-xs mt-2 px-3 py-1 font-semibold rounded-full ${getRiskColor(result.original_risk_level)}`}>{result.original_risk_level} Risk</p>
                       </div>

                       <ArrowRight className="h-8 w-8 text-muted-foreground hidden sm:block shrink-0" />

                       <div className="flex-1 flex flex-col items-center p-6 bg-primary/10 rounded-2xl border border-primary/30 shadow-[0_0_30px_rgba(var(--primary),0.15)] relative overflow-hidden">
                          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent pointer-events-none"></div>
                          <p className="text-sm font-medium text-primary uppercase tracking-widest mb-2 z-10">After</p>
                          <div className="text-4xl font-bold text-primary z-10">{(result.new_probability * 100).toFixed(1)}%</div>
                          <p className={`text-xs mt-2 px-3 py-1 font-semibold rounded-full z-10 ${getRiskColor(result.new_risk_level)}`}>{result.new_risk_level} Risk</p>
                       </div>

                    </div>

                    <div className="mt-6 grid grid-cols-2 gap-4">
                       <div className={`p-4 rounded-xl border flex flex-col items-center text-center ${result.absolute_change < 0 ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'}`}>
                         <span className="text-xs uppercase tracking-widest opacity-80 mb-1">Absolute Delta</span>
                         <span className="text-2xl font-bold">{(result.absolute_change * 100).toFixed(1)}%</span>
                       </div>
                       <div className={`p-4 rounded-xl border flex flex-col items-center text-center ${result.relative_change_pct < 0 ? 'bg-green-500/10 border-green-500/20 text-green-500' : 'bg-red-500/10 border-red-500/20 text-red-500'}`}>
                         <span className="text-xs uppercase tracking-widest opacity-80 mb-1">Relative Diff</span>
                         <span className="text-2xl font-bold">{result.relative_change_pct.toFixed(1)}%</span>
                       </div>
                    </div>

                    <div className="mt-6 flex-1 flex flex-col gap-4">
                       <div className="bg-secondary/40 p-4 rounded-xl border text-sm font-medium leading-relaxed">
                          {result.summary}
                       </div>
                       
                       <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                         <div className="border border-border/50 bg-card p-4 rounded-xl shadow-sm">
                           <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-2">New Top Reasons</h4>
                           <ul className="text-sm space-y-2">
                             {result.new_top_reasons?.map((r: string, i: number) => <li key={i} className="flex"><span className="text-red-400 mr-2">•</span>{r}</li>)}
                           </ul>
                         </div>
                         <div className="border border-primary/20 bg-primary/5 p-4 rounded-xl shadow-sm">
                           <h4 className="text-xs font-bold text-primary uppercase tracking-widest mb-2">Adjusted Actions</h4>
                           <ul className="text-sm space-y-2">
                             {result.recommended_actions?.map((a: string, i: number) => (
                               <li key={i} className="flex items-start">
                                 <CheckCircle2 className="h-4 w-4 mr-2 text-primary shrink-0 mt-0.5" />
                                 <span className="font-medium">{a}</span>
                               </li>
                             ))}
                           </ul>
                         </div>
                       </div>
                    </div>

                 </motion.div>
               )}
             </CardContent>
           </Card>
        </motion.div>
      </div>

    </div>
  );
}
