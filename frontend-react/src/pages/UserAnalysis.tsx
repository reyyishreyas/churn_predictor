import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { defaultCustomerPayload, predictUser } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Loader2, AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { toast } from 'sonner';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

export default function UserAnalysis() {
  const [formData, setFormData] = useState(defaultCustomerPayload);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await predictUser(formData);
      setResult(res);
      toast.success('Prediction generated successfully');
    } catch (err) {
      console.error(err);
      toast.error('Failed to get prediction from the backend API');
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
      
      {/* Left Column: Form */}
      <div className="w-full md:w-5/12 lg:w-1/3">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <Card className="rounded-2xl border-border/50 shadow-sm">
             <CardHeader>
               <CardTitle>User Profile</CardTitle>
               <CardDescription>Input customer metrics to predict their churn likelihood</CardDescription>
             </CardHeader>
             <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Customer ID</Label>
                    <Input className="bg-secondary/30 rounded-xl" value={formData.customer_id} onChange={e => setFormData({...formData, customer_id: e.target.value})} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Tenure (Months)</Label>
                      <Input type="number" className="bg-secondary/30 rounded-xl" value={formData.tenure} onChange={e => setFormData({...formData, tenure: parseInt(e.target.value)})} />
                    </div>
                    <div className="space-y-2">
                      <Label>Monthly Charges</Label>
                      <Input type="number" className="bg-secondary/30 rounded-xl" value={formData.MonthlyCharges} onChange={e => setFormData({...formData, MonthlyCharges: parseFloat(e.target.value)})} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Contract Type</Label>
                    <select 
                      className="flex h-10 w-full items-center justify-between rounded-xl border border-input bg-secondary/30 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                      value={formData.Contract} 
                      onChange={e => setFormData({...formData, Contract: e.target.value})}
                    >
                      <option value="Month-to-month">Month-to-month</option>
                      <option value="One year">One year</option>
                      <option value="Two year">Two year</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Days Since Login</Label>
                      <Input type="number" className="bg-secondary/30 rounded-xl" value={formData.days_since_last_login} onChange={e => setFormData({...formData, days_since_last_login: parseInt(e.target.value)})} />
                    </div>
                    <div className="space-y-2">
                      <Label>Session Duration</Label>
                      <Input type="number" className="bg-secondary/30 rounded-xl" value={formData.avg_session_duration_minutes} onChange={e => setFormData({...formData, avg_session_duration_minutes: parseFloat(e.target.value)})} />
                    </div>
                  </div>
                  <div className="space-y-2">
                      <Label>Feature Usage Score</Label>
                      <Input type="number" className="bg-secondary/30 rounded-xl" value={formData.feature_usage_score} onChange={e => setFormData({...formData, feature_usage_score: parseFloat(e.target.value)})} />
                  </div>
                  <Button type="submit" className="w-full rounded-xl h-11 mt-4" disabled={loading}>
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    {loading ? 'Analyzing...' : 'Predict Churn Risk'}
                  </Button>
                </form>
             </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Right Column: Result */}
      <div className="w-full md:w-7/12 lg:w-2/3">
         <AnimatePresence mode="wait">
            {!result && !loading ? (
               <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, y: -20 }} className="h-full min-h-[400px] flex items-center justify-center flex-col text-center border-2 border-dashed border-border/50 rounded-2xl bg-secondary/10">
                  <ShieldAlert className="h-16 w-16 text-muted-foreground/30 mb-4" />
                  <h3 className="text-xl font-semibold text-foreground/70">Awaiting Profile Data</h3>
                  <p className="text-muted-foreground mt-2 max-w-sm">Submit the form on the left to run our ML model and grab a real-time risk assessment.</p>
               </motion.div>
            ) : loading ? (
               <motion.div key="loading" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} className="h-full min-h-[400px] flex items-center justify-center">
                  <div className="flex flex-col items-center">
                    <div className="relative">
                       <div className="h-24 w-24 rounded-full border-4 border-secondary border-t-primary animate-spin"></div>
                       <div className="absolute inset-0 flex items-center justify-center">
                         <div className="h-16 w-16 rounded-full bg-primary/10 animate-pulse"></div>
                       </div>
                    </div>
                    <p className="mt-6 text-foreground font-medium animate-pulse">Executing ML Pipeline...</p>
                  </div>
               </motion.div>
            ) : (
               <motion.div key="result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 gap-6">
                 
                 <Card className="rounded-2xl border-border/50 shadow-soft-dark overflow-hidden relative">
                   <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 blur-3xl rounded-full -mr-20 -mt-20 pointer-events-none"></div>
                   <CardContent className="p-8">
                      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                         <div>
                            <p className="text-sm font-medium text-muted-foreground uppercase tracking-widest mb-1">Churn Probability</p>
                            <div className="text-7xl font-bold tracking-tighter">
                               {(result.churn_probability * 100).toFixed(1)}%
                            </div>
                         </div>
                         <div className="flex flex-col items-end gap-3 rounded-2xl bg-secondary/30 p-5 min-w-[250px]">
                           <Badge className={`px-4 py-1.5 text-sm font-semibold rounded-full ${getRiskColor(result.risk_level)}`}>
                             {result.risk_level} Risk Level
                           </Badge>
                           <p className="text-sm font-medium text-foreground">Engagement: <span className="text-muted-foreground">{result.engagement_score} ({result.engagement_label})</span></p>
                           <p className="text-sm font-medium text-foreground">Segment: <span className="text-muted-foreground">{result.segment}</span></p>
                           <p className="text-sm font-medium justify-between text-foreground">Auto Triggered: <span className={result.auto_triggered ? "text-primary" : "text-muted-foreground"}>{result.auto_triggered ? "Yes" : "No"}</span></p>
                         </div>
                      </div>
                   </CardContent>
                 </Card>

                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card className="rounded-2xl border-border/50 shadow-sm bg-card">
                       <CardHeader>
                         <CardTitle className="text-lg">Key Risk Factors</CardTitle>
                       </CardHeader>
                       <CardContent>
                         <ul className="space-y-3">
                           {result.top_reasons?.map((reason: string, i: number) => (
                             <motion.li initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 * i }} key={i} className="flex items-center text-sm p-3 rounded-xl bg-red-500/5 text-red-500 font-medium">
                               <AlertCircle className="h-4 w-4 mr-3 shrink-0" />
                               {reason}
                             </motion.li>
                           ))}
                         </ul>
                         
                         <div className="mt-6">
                           <h4 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-3">Strategy</h4>
                           <p className="text-sm text-foreground bg-secondary/40 p-4 rounded-xl border border-border/50 leading-relaxed">{result.strategy}</p>
                         </div>
                       </CardContent>
                    </Card>

                    <Card className="rounded-2xl border-[1px] border-primary/20 shadow-sm bg-gradient-to-b from-card to-primary/[0.02]">
                       <CardHeader>
                         <CardTitle className="text-lg text-primary">Local Explainability</CardTitle>
                       </CardHeader>
                       <CardContent>
                          <div className="h-[250px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart
                                layout="vertical"
                                data={[...result.explainability].sort((a, b) => b.contribution_pct - a.contribution_pct)}
                                margin={{ top: 0, right: 20, left: 20, bottom: 0 }}
                              >
                                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="var(--border)" />
                                <XAxis type="number" hide />
                                <YAxis dataKey="feature" type="category" width={100} fontSize={11} tickLine={false} axisLine={false} stroke="#888" tickFormatter={(v) => v.replace('_', ' ')} />
                                <Tooltip cursor={{fill: 'var(--secondary)'}} contentStyle={{ borderRadius: '12px', border: '1px solid var(--border)', backgroundColor: 'var(--card)' }} />
                                <Bar dataKey="contribution_pct" radius={[0, 4, 4, 0]}>
                                  {result.explainability.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={entry.direction === 'increase' ? '#ef4444' : '#3b82f6'} />
                                  ))}
                                </Bar>
                              </BarChart>
                            </ResponsiveContainer>
                          </div>
                          
                          <div className="mt-4 border-t border-border/50 pt-4">
                             <h4 className="text-sm font-bold text-primary mb-2">Recommended Actions</h4>
                             <ul className="space-y-2">
                               {result.recommended_actions?.map((action: string, i: number) => (
                                 <li key={i} className="flex items-center text-sm font-medium">
                                   <CheckCircle2 className="h-4 w-4 mr-2 text-primary" /> {action}
                                 </li>
                               ))}
                             </ul>
                          </div>
                          
                       </CardContent>
                    </Card>
                 </div>
               </motion.div>
            )}
         </AnimatePresence>
      </div>

    </div>
  );
}
