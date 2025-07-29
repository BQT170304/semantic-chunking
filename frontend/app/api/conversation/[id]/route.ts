import { NextRequest, NextResponse } from "next/server";

const SERVER_BASE_URL = process.env.QUERY_SERVER_BASE_URL || "http://localhost:8000";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const targetUrl = `${SERVER_BASE_URL}/conversations/${params.id}`;

    const response = await fetch(targetUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const result = await response.text();
    return new NextResponse(result, {
      status: response.status,
    });
  } catch (error) {
    console.error("Error in API proxy route:", error);
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204, // No Content
    headers: {
      "Access-Control-Allow-Origin": "*", // Be more specific in production if needed
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization", // Adjust as per client's request headers
    },
  });
}
