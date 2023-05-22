package com.example.demoXM.helper;

import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpSession;

import com.example.demoXM.entity.User;

public class SessionHelper {
	//所有客户端的session的权限保存在这里
	//key: session   value: 权限
	private static Map<HttpSession,User> sessionRoleMap = new HashMap<>();

	//保存客戶端權限
	public static void addSessionRole(HttpSession session, User user) {
		sessionRoleMap.put(session, user);
	}

	//取得客戶端權限
	public static User getSessionRole(HttpSession session) {
		return sessionRoleMap.get(session);
	}

	//取得客戶端權限
	public static void deleteSessionRole(HttpSession session) {
		 sessionRoleMap.remove(session);
	}
}
