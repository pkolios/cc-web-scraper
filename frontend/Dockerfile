FROM node:9-alpine as builder

RUN npm install -g @angular/cli

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN ng build --prod

FROM nginx:1.13-alpine

COPY nginx/default.conf /etc/nginx/conf.d/

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /usr/src/app/dist/ng-app /usr/share/nginx/html
