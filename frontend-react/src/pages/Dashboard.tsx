import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Users, AlertTriangle, Activity, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { getInsights } from '@/lib/api';

export default function Dashboard() {
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
        // Fallback for UI skeleton dev if backend is unvailable
        setTimeout(() => setLoading(false), 2000);
      });
  }, []);

  const container: any = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item: any = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  const RISK_COLORS = { Low: "#10b981", Medium: "#f59e0b", High: "#ef4444" };
  const ENGAGE_COLORS = { Low: "#ef4444", Moderate: "#f59e0b", High: "#3b82f6" };

  return (
    <div className="flex flex-col space-y-8 w-full max-w-[1400px] mx-auto pb-10">
      <div className="flex flex-col md:flex-row shadow-none items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground shadow-none">Dashboard</h1>
          <p className="text-muted-foreground mt-1 shadow-none">Real-time metrics and overall platform health.</p>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-2xl" />
          ))}
        </div>
      ) : (
        <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div variants={item}>
            <Card className="rounded-2xl border-border/50 shadow-sm bg-card hover:shadow-soft-dark transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Users</CardTitle>
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Users className="h-4 w-4 text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{data?.total_users ? data.total_users.toLocaleString() : '12,345'}</div>
                <p className="text-xs text-muted-foreground mt-1 text-green-500 font-medium">+4.2% from last month</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="rounded-2xl border-border/50 shadow-sm bg-card hover:shadow-soft-dark transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">Observed Churn Rate</CardTitle>
                <div className="h-8 w-8 rounded-full bg-red-500/10 flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-red-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{(data?.overall_churn_rate * 100).toFixed(1) || '14.2'}%</div>
                <p className="text-xs text-muted-foreground mt-1 text-red-500 font-medium">+1.1% from last month</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="rounded-2xl border-border/50 shadow-sm bg-card hover:shadow-soft-dark transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">Mean Risk</CardTitle>
                <div className="h-8 w-8 rounded-full bg-yellow-500/10 flex items-center justify-center">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{(data?.churn_probability_summary?.mean * 100).toFixed(1) || '24.5'}%</div>
                <p className="text-xs text-muted-foreground mt-1">Average predicted probability</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={item}>
            <Card className="rounded-2xl border-border/50 shadow-sm bg-card hover:shadow-soft-dark transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">P90 Risk Level</CardTitle>
                <div className="h-8 w-8 rounded-full bg-blue-500/10 flex items-center justify-center">
                  <Activity className="h-4 w-4 text-blue-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{(data?.churn_probability_summary?.p90 * 100).toFixed(1) || '68.0'}%</div>
                <p className="text-xs text-muted-foreground mt-1">Top 10% highest risk bucket</p>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-20">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card className="col-span-1 rounded-2xl border-border/50 shadow-sm bg-card">
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
              <CardDescription>Breakdown of users by predicted churn risk</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? <Skeleton className="h-[300px] w-full rounded-xl" /> : (
                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(data?.predicted_risk_distribution || { Low: 500, Medium: 300, High: 150 }).map(([k, v]) => ({ name: k, value: v }))}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                      <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: '12px', border: '1px solid var(--border)', backgroundColor: 'var(--card)' }} />
                      <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                        {Object.keys(data?.predicted_risk_distribution || { Low: 0, Medium: 0, High: 0 }).map((entry: any, index) => (
                          <Cell key={`cell-${index}`} fill={(RISK_COLORS as any)[entry] || RISK_COLORS.Low} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card className="col-span-1 rounded-2xl border-border/50 shadow-sm bg-card">
            <CardHeader>
              <CardTitle>Engagement Distribution</CardTitle>
              <CardDescription>Segmenting user activity level</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? <Skeleton className="h-[300px] w-full rounded-xl" /> : (
                <div className="h-[300px] w-full flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={Object.entries(data?.engagement_distribution || { High: 400, Moderate: 350, Low: 200 }).map(([k, v]) => ({ name: k, value: v }))}
                        cx="50%"
                        cy="50%"
                        innerRadius={80}
                        outerRadius={110}
                        paddingAngle={5}
                        dataKey="value"
                        stroke="none"
                      >
                        {Object.keys(data?.engagement_distribution || { High: 0, Moderate: 0, Low: 0 }).map((entry: any, index) => (
                          <Cell key={`cell-${index}`} fill={(ENGAGE_COLORS as any)[entry] || ENGAGE_COLORS.Low} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid var(--border)', backgroundColor: 'var(--card)' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
