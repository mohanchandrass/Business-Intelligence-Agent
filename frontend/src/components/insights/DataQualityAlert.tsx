import React from "react";
import { DataQualityIssue } from "@/contracts/api";
import { AlertTriangle, Info, XOctagon } from "lucide-react";

interface DataQualityAlertProps {
  issues: DataQualityIssue[];
}

export function DataQualityAlert({ issues }: DataQualityAlertProps) {
  if (!issues || issues.length === 0) return null;

  return (
    <div className="flex flex-col gap-2 mt-6">
      {issues.map((issue, idx) => {
        let bgColor = "bg-muted/10";
        let borderColor = "border-muted/20";
        let textColor = "text-muted";
        let Icon = Info;

        if (issue.severity === "warning") {
          bgColor = "bg-orange/10";
          borderColor = "border-orange/20";
          textColor = "text-orange";
          Icon = AlertTriangle;
        } else if (issue.severity === "error") {
          bgColor = "bg-red/10";
          borderColor = "border-red/20";
          textColor = "text-red";
          Icon = XOctagon;
        }

        return (
          <div
            key={idx}
            className={`flex gap-3 p-3 rounded-lg border ${bgColor} ${borderColor}`}
          >
            <Icon className={`w-5 h-5 shrink-0 ${textColor}`} />
            <div className="flex flex-col">
              <span className={`text-sm font-medium ${textColor} mb-1`}>
                Data quality {issue.severity}
              </span>
              <p className="text-sm text-foreground">{issue.message}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
