/** Design-only interfaces. No production adapter is connected in v0.1.0. */
export type ExecutionStatus = 'queued'|'running'|'needs_approval'|'paused'|'failed'|'completed'|'cancelled';
export type ResultOrigin = 'local_result'|'preview_only'|'remote_result';
export interface ArtifactRef { id: string; versionId: string; contentHash?: string; }
export interface CapabilityRequest {
  requestId: string; taskId: string; capability: string;
  inputArtifactRefs: readonly ArtifactRef[]; userIntent: string;
  grantedScopes: readonly string[]; deadline: string; idempotencyKey: string;
  requireApproval: boolean;
}
export interface Approval {
  actionId: string; taskId: string; versionId: string; expiresAt: string;
  payloadHash: string; recipient?: string; maxCost?: { currency: string; amount: number };
}
export interface TaskEvent {
  eventId: string; taskId: string; sequence: number; serverTime: string;
  origin: ResultOrigin; status: ExecutionStatus; step?: string;
  outputs?: readonly ArtifactRef[];
  error?: { code: string; message: string; canRetry: boolean; irreversibleEffects?: string[] };
}
export interface CapabilityAdapter {
  execute(request: CapabilityRequest, signal: AbortSignal): AsyncIterable<TaskEvent>;
  confirm(approval: Approval, signal: AbortSignal): Promise<TaskEvent>;
  cancel(taskId: string, signal: AbortSignal): Promise<TaskEvent>;
}
