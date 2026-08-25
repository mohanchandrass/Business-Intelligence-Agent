import React from "react";
import { LineVisualization } from "@/contracts/api";
import { Card } from "../ui/Card";
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

interface LineChartProps {
  data: LineVisualization;
}

export function LineChart({ data }: LineChartProps) {
  return (
    <Card className="p-4 w-full h-[300px]">
      <h3 className="text-sm font-medium text-foreground mb-4">{data.title}</h3>
      <div className="w-full h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <RechartsLineChart
            data={data.data}
            margin={{ top: 5, right: 10, left: 0, bottom: 20 }}
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
              contentStyle={{ borderRadius: '8px', border: '1px solid var(--color-border)', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}
              itemStyle={{ color: 'var(--color-primary)', fontWeight: 500 }}
              labelStyle={{ color: 'var(--color-muted)', marginBottom: '4px' }}
              formatter={(value: any) => {
                return [
                  data.unit === 'INR' ? `₹${value.toLocaleString()}` : value.toLocaleString(),
                  "Value"
                ];
              }}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="var(--color-primary)" 
              strokeWidth={2}
              activeDot={{ r: 6, fill: 'var(--color-primary)', stroke: 'white', strokeWidth: 2 }}
              dot={false}
            />
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
