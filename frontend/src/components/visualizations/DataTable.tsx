import React from "react";
import { TableVisualization } from "@/contracts/api";
import { Card } from "../ui/Card";

interface DataTableProps {
  data: TableVisualization;
}

export function DataTable({ data }: DataTableProps) {
  return (
    <Card className="overflow-hidden w-full">
      {data.title && (
        <div className="p-4 border-b border-border">
          <h3 className="text-sm font-medium text-foreground">{data.title}</h3>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-background text-muted text-xs uppercase tracking-wider">
            <tr>
              {data.columns.map((col, idx) => (
                <th key={idx} className="px-4 py-3 font-medium">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.data.map((row, rowIdx) => (
              <tr key={rowIdx} className="hover:bg-background/50">
                {data.columns.map((col, colIdx) => (
                  <td key={colIdx} className="px-4 py-3 text-foreground">
                    {renderCell(col, row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function renderCell(columnName: string, value: any) {
  const lowerCol = columnName.toLowerCase();
  
  if (lowerCol === "status" || lowerCol.includes("state")) {
    let colorClass = "bg-muted/10 text-muted";
    const strVal = String(value).toLowerCase();
    
    if (strVal.includes("done") || strVal.includes("success") || strVal.includes("completed")) {
      colorClass = "bg-green/10 text-green";
    } else if (strVal.includes("risk") || strVal.includes("blocked") || strVal.includes("delayed")) {
      colorClass = "bg-red/10 text-red";
    } else if (strVal.includes("progress") || strVal.includes("working")) {
      colorClass = "bg-orange/10 text-orange";
    }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colorClass}`}>
        {value}
      </span>
    );
  }

  return value;
}
