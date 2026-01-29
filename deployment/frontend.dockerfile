FROM node:25-alpine AS builder

WORKDIR /app
COPY ../frontend .
RUN npm install
RUN npm run build

FROM nginx:1.29-alpine

RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
COPY deployment/nginx-frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
