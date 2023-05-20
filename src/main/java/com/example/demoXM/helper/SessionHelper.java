package com.example.demoXM.helper;

import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpSession;

public class SessionHelper {
	//所有客户端的session的权限保存在这里
	//key: session   value: 权限
	private static Map<HttpSession, String> sessionRoleMap = new HashMap<>();

	//保存客戶端權限
	public static void addSessionRole(HttpSession session, String role) {
		sessionRoleMap.put(session, role);
	}

	//取得客戶端權限
	public static String getSessionRole(HttpSession session) {
		return sessionRoleMap.get(session);
	}

	//取得客戶端權限
	public static String deleteSessionRole(HttpSession session) {
		return sessionRoleMap.remove(session);
	}
}
