const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(
    message: string,
    status: number,
    details: unknown = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}


function formatErrorDetail(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item && typeof item === "object") {
          const obj = item as Record<string, unknown>;

          const location = Array.isArray(obj.loc)
            ? obj.loc.join(" -> ")
            : "";

          const message =
            typeof obj.msg === "string"
              ? obj.msg
              : JSON.stringify(obj);

          return location
            ? `${location}: ${message}`
            : message;
        }

        return String(item);
      })
      .join("\n");
  }

  if (detail && typeof detail === "object") {
    try {
      return JSON.stringify(detail, null, 2);
    } catch {
      return "Request failed";
    }
  }

  if (detail !== undefined && detail !== null) {
    return String(detail);
  }

  return "Request failed";
}


function getErrorMessage(data: unknown): string {
  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>;

    if ("detail" in obj) {
      return formatErrorDetail(obj.detail);
    }

    if ("message" in obj) {
      return formatErrorDetail(obj.message);
    }

    if ("error" in obj) {
      return formatErrorDetail(obj.error);
    }
  }

  return formatErrorDetail(data);
}


async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem("seatflow_token");

  const headers = new Headers(options.headers);

  if (
    options.body &&
    !headers.has("Content-Type")
  ) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  let response: Response;

  try {
    response = await fetch(
      `${API_BASE}${path}`,
      {
        ...options,
        headers,
      },
    );
  } catch {
    throw new ApiError(
      `Cannot connect to SeatFlow API at ${API_BASE}. Make sure FastAPI is running.`,
      0,
    );
  }

  const contentType =
    response.headers.get("content-type") || "";

  let data: unknown = null;

  if (
    contentType.includes(
      "application/json",
    )
  ) {
    try {
      data = await response.json();
    } catch {
      data = null;
    }
  } else {
    try {
      data = await response.text();
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    throw new ApiError(
      getErrorMessage(data),
      response.status,
      data,
    );
  }

  return data as T;
}


// ============================================================
// TYPES
// ============================================================

export interface User {
  id: number;
  restaurant_id: number;
  email: string;
  role: string;
  is_active: boolean;
}


export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}


export interface WaitlistEntry {
  id: number;
  restaurant_id: number;
  customer_name: string;
  phone: string;
  party_size: number;
  status: string;
  estimated_wait_minutes: number;
  created_at: string;
}


export interface Statistics {
  total: number;
  waiting: number;
  notified: number;
  seated: number;
  cancelled: number;
  no_show: number;
}


// ============================================================
// TOKEN HELPERS
// ============================================================

export function setToken(
  token: string,
): void {
  localStorage.setItem(
    "seatflow_token",
    token,
  );
}


export function saveToken(
  token: string,
): void {
  setToken(token);
}


export function getToken(): string | null {
  return localStorage.getItem(
    "seatflow_token",
  );
}


export function clearToken(): void {
  localStorage.removeItem(
    "seatflow_token",
  );
}


// ============================================================
// AUTHENTICATION
// ============================================================

export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>(
    "/api/auth/login",
    {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
      }),
    },
  );
}


export async function register(
  restaurantName: string,
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>(
    "/api/auth/register",
    {
      method: "POST",
      body: JSON.stringify({
        restaurant_name: restaurantName,
        email,
        password,
      }),
    },
  );
}


export async function getMe(): Promise<User> {
  return request<User>(
    "/api/auth/me",
  );
}


// ============================================================
// WAITLIST
// ============================================================

export async function getWaitlist(): Promise<
  WaitlistEntry[]
> {
  return request<WaitlistEntry[]>(
    "/api/waitlist",
  );
}


export async function addParty(
  customerName: string,
  phone: string,
  partySize: number,
): Promise<WaitlistEntry> {
  return request<WaitlistEntry>(
    "/api/waitlist",
    {
      method: "POST",
      body: JSON.stringify({
        customer_name: customerName,
        phone,
        party_size: partySize,
      }),
    },
  );
}


export async function addWaitlistEntry(
  payload: {
    customer_name: string;
    phone: string;
    party_size: number;
  },
): Promise<WaitlistEntry> {
  return addParty(
    payload.customer_name,
    payload.phone,
    payload.party_size,
  );
}


export async function callNext(): Promise<
  WaitlistEntry
> {
  return request<WaitlistEntry>(
    "/api/waitlist/call-next",
    {
      method: "POST",
    },
  );
}


export async function seatParty(
  entryId: number,
): Promise<WaitlistEntry> {
  return request<WaitlistEntry>(
    `/api/waitlist/${entryId}/seat`,
    {
      method: "POST",
    },
  );
}


export async function cancelParty(
  entryId: number,
): Promise<WaitlistEntry> {
  return request<WaitlistEntry>(
    `/api/waitlist/${entryId}/cancel`,
    {
      method: "POST",
    },
  );
}


export async function noShowParty(
  entryId: number,
): Promise<WaitlistEntry> {
  return request<WaitlistEntry>(
    `/api/waitlist/${entryId}/no-show`,
    {
      method: "POST",
    },
  );
}


export async function getStatistics(): Promise<
  Statistics
> {
  return request<Statistics>(
    "/api/waitlist/statistics/summary",
  );
}
