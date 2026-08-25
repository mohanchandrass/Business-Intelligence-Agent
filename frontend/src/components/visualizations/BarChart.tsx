import React from "react";
import { BarVisualization } from "@/contracts/api";
import { Card } from "../ui/Card";
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

interface BarChartProps {
  data: BarVisualization;
}

export function BarChart({ data }: BarChartProps) {
  return (
    <Card className="p-4 w-full h-[300px]">
      <h3 className="text-sm font-medium text-foreground mb-4">{data.title}</h3>
      <div className="w-full h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <RechartsBarChart
            data={data.data}
            margin={{ top: 5, right: 10, left: 0, bottom: 20 }}
            barSize={32}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" />
            <XAxis 
              dataKey="label" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--color-muted)', fontSize: 12 }} 
              dy={10}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'var(--color-muted)', fontSize: 12 }}
              tickFormatter={(value) => {
                if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
                if (value >= 1000) return `${(value / 1000).toFixed(0)}k`;
                return value;
              }}
            />
            <Tooltip 
              cursor={{ fill: 'var(--color-background)' }}
              contentStyle={{ borderRadius: '8px', border: '1px solid var(--color-border)', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}
              itemStyle={{ color: 'var(--color-foreground)', fontWeight: 500 }}
              labelStyle={{ color: 'var(--color-muted)', marginBottom: '4px' }}
              formatter={(value: any) => [
                data.config.yAxisFormat === 'currency' 
                  ? `₹${value.toLocaleString()}` : value.toLocaleString(),
                  "Value"
                ]}
            />
            <Bar dataKey="value" fill="var(--color-primary)" radius={[4, 4, 0, 0]} />
          </RechartsBarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
