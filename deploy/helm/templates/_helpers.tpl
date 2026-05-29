{{- define "mdf.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "mdf.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "mdf.labels" -}}
helm.sh/chart: {{ include "mdf.name" . }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "mdf.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "mdf.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mdf.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "mdf.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "mdf.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{- define "mdf.databaseHost" -}}
{{- if .Values.database.host -}}
{{- .Values.database.host -}}
{{- else -}}
{{- printf "%s-postgresql" .Release.Name -}}
{{- end -}}
{{- end -}}

{{- define "mdf.databaseUrl" -}}
{{- printf "postgresql+psycopg://%s:%s@%s:%v/%s?sslmode=%s" .Values.database.username .Values.database.password (include "mdf.databaseHost" .) .Values.database.port .Values.database.name .Values.database.sslMode -}}
{{- end -}}

{{- define "mdf.env" -}}
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ default (printf "%s-database" (include "mdf.fullname" .)) .Values.database.existingSecret }}
      key: {{ .Values.database.existingSecretKey }}
- name: MLFLOW_TRACKING_URI
  value: {{ printf "http://%s-mlflow:5000" (include "mdf.fullname" .) | quote }}
{{- end -}}

