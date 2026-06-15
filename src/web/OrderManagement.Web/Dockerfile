# Multi-stage image for the .NET 8 BFF + the React (Vite) UI it serves.
#
# Stage 1: build the React app into /wwwroot.
# Stage 2: restore + publish the ASP.NET Core app, embedding /wwwroot.
# Stage 3: small ASP.NET runtime image.
#
# Build context = this project folder (src/web/OrderManagement.Web), so ClientApp
# is available as a subfolder.

# ---- Stage 1: React build ----
FROM node:20-alpine AS client
WORKDIR /client
COPY ClientApp/package*.json ./
RUN npm ci
COPY ClientApp/ ./
# vite.config.ts has outDir "../wwwroot" => from /client that resolves to /wwwroot.
RUN npm run build

# ---- Stage 2: .NET publish ----
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY OrderManagement.Web.csproj ./
RUN dotnet restore OrderManagement.Web.csproj
COPY . ./
# Bring in the freshly built SPA assets.
COPY --from=client /wwwroot ./wwwroot
RUN dotnet publish OrderManagement.Web.csproj -c Release -o /app

# ---- Stage 3: runtime ----
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app ./
ENV ASPNETCORE_URLS=http://+:5080
# Default downstream API location; override in compose / at runtime.
ENV PythonApi__BaseUrl=http://api:5001
EXPOSE 5080
ENTRYPOINT ["dotnet", "OrderManagement.Web.dll"]
