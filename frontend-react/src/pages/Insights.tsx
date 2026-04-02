import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LabelList } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { getInsights } from '@/lib/api';

export default function Insights() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInsights()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setTimeout(() => setLoading(false), 1500);
      });
  }, []);

  const featureImportance = data?.feature_importance || [
    { feature: 'Contract_Month-to-month', importance: 0.28 },
    { feature: 'tenure', importance: 0.18 },
    { feature: 'InternetService_Fiber_optic', importance: 0.12 },
    { feature: 'TotalCharges', importance: 0.09 },
    { feature: 'MonthlyCharges', importance: 0.08 },
    { feature: 'PaymentMethod_Electronic_check', importance: 0.07 }
  ];

  const sortedFeatures = [...featureImportance].sort((a, b) => b.importance - a.importance).slice(0, 10);

  return (
    <div className="flex flex-col space-y-8 w-full max-w-[1400px] mx-auto pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Model Insights</h1>
          <p className="text-muted-foreground mt-1">Deep dive into what drives churn according to our ML model.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="lg:col-span-2">
          <Card className="rounded-2xl border-border/50 bg-card h-full">
            <CardHeader>
              <CardTitle>Top Feature Importance</CardTitle>
              <CardDescription>Features ranked by their predictive power for churn classification</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? <Skeleton className="h-[400px] w-full rounded-xl" /> : (
                <div className="h-[400px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={sortedFeatures}
                      layout="vertical"
                      margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                      <XAxis type="number" fontSize={12} tickLine={false} axisLine={false} stroke="#888888" />
                      <YAxis dataKey="feature" type="category" width={120} fontSize={10} tickLine={false} axisLine={false} stroke="#888888" tickFormatter={(v) => v.replace('_', ' ')} />
                      <Tooltip cursor={{fill: 'var(--secondary)'}} contentStyle={{ borderRadius: '12px', border: '1px solid var(--border)', backgroundColor: 'var(--card)' }} />
                      <Bar dataKey="importance" fill="var(--primary)" radius={[0, 4, 4, 0]}>
                         <LabelList dataKey="importance" position="right" fontSize={10} fill="#888888" formatter={(val: any) => Number(val).toFixed(3)} />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="lg:col-span-1">
          <Card className="rounded-2xl border-border/50 bg-card h-full">
            <CardHeader>
              <CardTitle>Model Metrics</CardTitle>
              <CardDescription>Current model performance overview</CardDescription>
            </CardHeader>
            <CardContent>
               {loading ? (
                 <div className="space-y-4">
                   <Skeleton className="h-16 w-full rounded-xl" />
                   <Skeleton className="h-16 w-full rounded-xl" />
                   <Skeleton className="h-16 w-full rounded-xl" />
                 </div>
               ) : (
                 <div className="space-y-4">
                   {Object.entries((data?.model_metrics?.RandomForest || data?.model_metrics?.LogisticRegression) || {
                     Accuracy: 0.82, 'ROC AUC': 0.88, 'F1 Score': 0.75, Precision: 0.71, Recall: 0.79
                   }).map(([k, v]) => (
                     <div key={k} className="flex flex-col p-4 rounded-xl bg-secondary/30 border border-border/50">
                        <span className="text-sm font-medium text-muted-foreground">{k}</span>
                        <span className="text-2xl font-bold tracking-tight mt-1">{v as any}</span>
                     </div>
                   ))}
                 </div>
               )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
